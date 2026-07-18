"""后端 HTTP 客户端（契约 §4）—— httpx 封装 + 信封解包。

覆盖设备侧端点：
- `POST /rollcall/device-checkins`（核心签到，§4.1）
- `GET /devices/me/roster`（离线兜底名单，§4.2）
- `GET /devices/me/audio-manifest` + `GET /devices/me/audio/{file}`（音频差量下载，§4.3）
- `POST /devices/me/heartbeat`（心跳兜底，§4.4）

一切请求带 `Authorization: Bearer <device JWT>`（AuthManager 提供，过期自动续期）。
网络失败 / 5xx 抛 `NetworkError`，由上层转离线队列。
"""

from __future__ import annotations

import hashlib
import logging
import os
import re
from pathlib import Path

import httpx

from .auth import AuthManager
from .envelope import ApiResponse, NetworkError, unwrap

logger = logging.getLogger(__name__)

# 音频文件名白名单 —— 与后端 devices.py 的 _AUDIO_NAME_RE 同款（防路径穿越，纵深防御）
_AUDIO_NAME_RE = re.compile(r"^[A-Za-z0-9_.-]+\.wav$")


class ApiClient:
    """设备侧后端调用封装。"""

    def __init__(
        self,
        base_url: str,
        auth: AuthManager,
        http: httpx.Client,
        fw_version: str = "rollcall-device-unknown",
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._auth = auth
        self._http = http
        self._fw_version = fw_version

    def _get(self, path: str) -> ApiResponse:
        try:
            resp = self._http.get(
                f"{self._base_url}{path}", headers=self._auth.auth_header()
            )
        except httpx.HTTPError as exc:
            raise NetworkError(str(exc)) from exc
        return unwrap(resp)

    def _post(self, path: str, body: dict) -> ApiResponse:
        try:
            resp = self._http.post(
                f"{self._base_url}{path}", json=body, headers=self._auth.auth_header()
            )
        except httpx.HTTPError as exc:
            raise NetworkError(str(exc)) from exc
        return unwrap(resp)

    # --------------------------- §4.1 签到 ---------------------------

    def post_checkin(self, body: dict) -> ApiResponse:
        """上报一次签到（契约 §4.1）。网络失败 / 5xx → NetworkError（触发离线降级）。"""
        return self._post("/api/v1/rollcall/device-checkins", body)

    # --------------------------- §4.2 名单 ---------------------------

    def fetch_roster(self) -> tuple[str, list[dict]]:
        """拉离线兜底名单，返回 (generated_at, students)（契约 §4.2）。"""
        resp = self._get("/api/v1/devices/me/roster")
        if not resp.ok:
            raise NetworkError(f"拉名单失败：{resp.error_code}")
        data = resp.data or {}
        return data.get("generated_at", ""), data.get("students", []) or []

    # --------------------------- §4.3 音频 ---------------------------

    def fetch_audio_manifest(self) -> list[dict]:
        """拉音频清单 `[{name, sha256, size}]`（契约 §4.3）。"""
        resp = self._get("/api/v1/devices/me/audio-manifest")
        if not resp.ok:
            raise NetworkError(f"拉音频清单失败：{resp.error_code}")
        return (resp.data or {}).get("files", []) or []

    def download_audio(self, file_name: str, dest: Path) -> None:
        """下载单个音频文件到 dest（契约 §4.3；音频原文件不走信封，直接是 wav 字节）。"""
        try:
            resp = self._http.get(
                f"{self._base_url}/api/v1/devices/me/audio/{file_name}",
                headers=self._auth.auth_header(),
            )
        except httpx.HTTPError as exc:
            raise NetworkError(str(exc)) from exc
        if resp.status_code >= 400:
            raise NetworkError(f"下载音频 {file_name} 失败：HTTP {resp.status_code}")
        dest.parent.mkdir(parents=True, exist_ok=True)
        tmp = dest.with_suffix(dest.suffix + ".tmp")
        tmp.write_bytes(resp.content)
        tmp.replace(dest)

    def sync_audio(self, cache_dir: Path) -> int:
        """对照 manifest 差量下载（sha256 不一致 / 缺失才下），返回本次下载数。契约 §4.3。"""
        cache_dir = Path(cache_dir)
        cache_dir.mkdir(parents=True, exist_ok=True)
        downloaded = 0
        for entry in self.fetch_audio_manifest():
            name = entry.get("name")
            want_sha = entry.get("sha256")
            if not name:
                continue
            # 设备侧独立校验文件名（纵深防御 — 后端已有同款白名单，但被攻破 / manifest 出错时
            # 不能让 "../../etc/foo.wav" 写到缓存目录外。正则与后端 _AUDIO_NAME_RE 同款）
            if not _AUDIO_NAME_RE.match(name):
                logger.warning("[audio] manifest 含非法文件名，已跳过：%r", name)
                continue
            local = cache_dir / name
            # resolve 后再确认仍在 cache_dir 下（软链接 / 奇异路径的兜底）
            if not str(local.resolve()).startswith(str(cache_dir.resolve()) + os.sep):
                logger.warning("[audio] 文件名解析后越出缓存目录，已跳过：%r", name)
                continue
            if local.exists() and want_sha and _sha256_file(local) == want_sha:
                continue
            self.download_audio(name, local)
            downloaded += 1
        return downloaded

    # --------------------------- §4.4 心跳 ---------------------------

    def heartbeat(self) -> ApiResponse:
        """HTTP 心跳兜底（WS 不可用时用，契约 §4.4）。"""
        return self._post(
            "/api/v1/devices/me/heartbeat", {"fw_version": self._fw_version}
        )


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()
