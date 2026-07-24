import React from "react";
import { RYO } from "../theme";
import { api } from "../api/client";
import type { RegistrationCode } from "../api/types";

// Task #14 学生登录码（学生登録コード）面板
// 来源：WEB_DESIGN_LOG §11.9.1 + system_features.md §7.16（5-03 itsuki 拍板）
// 目的：App Store 公开后通过 6 位有效期 5 分钟的码做学生注册 gate
// 权限（2026-06-14 itsuki 拍板）：所有权限组都能完整使用，演示账号也可用 → 后端不再返回 403。
//   下面 forbidden 分支保留作兜底（防御后端意外 403），正常路径不会触发。
// 跟 iOS 对齐：iOS RegisterStep5 已使用注册码（5-26 A-035 修复时改成真接 backend）
// 源 index.html 13694-14143（components/registration-code-panel.jsx 块）。界面原样搬，仅作用域引用方式改写。
export function RegistrationCodePanel({ authToken }: { authToken: string }) {
  const T = RYO;
  const [code, setCode] = React.useState<string | null>(null);
  const [expiresAt, setExpiresAt] = React.useState<number | null>(null);
  const [createdAt, setCreatedAt] = React.useState<string | null>(null);
  const [loading, setLoading] = React.useState(false);
  const [refreshing, setRefreshing] = React.useState(false);
  const [refreshLockUntil, setRefreshLockUntil] = React.useState(0);
  const [forbidden, setForbidden] = React.useState(false);
  const [err, setErr] = React.useState("");
  const [now, setNow] = React.useState(Date.now());
  const [confirm, setConfirm] = React.useState(false);
  const [copyToast, setCopyToast] = React.useState(false);
  // web#113：复制成功 toast 的定时器 — 用 ref 存 id，卸载时清掉，避免已卸载 setState
  const copyToastTimerRef = React.useRef<ReturnType<typeof setTimeout> | null>(
    null,
  );
  // 请求代次守卫 — 防迟到的轮询响应用已失效旧码覆盖 doRefresh 刚生成的新码
  const fetchGenRef = React.useRef(0);

  // 倒计时刷新 — 每秒重算 expiresAt - now
  React.useEffect(() => {
    const id = setInterval(() => setNow(Date.now()), 1000);
    return () => clearInterval(id);
  }, []);

  // 卸载时清掉复制 toast 定时器
  React.useEffect(() => {
    return () => {
      if (copyToastTimerRef.current != null) {
        clearTimeout(copyToastTimerRef.current);
        copyToastTimerRef.current = null;
      }
    };
  }, []);

  // 30 秒一次 polling — 检测其他老师在另一终端重新生成的情况（§11.9.1 拍板）
  const fetchCurrent = React.useCallback(async () => {
    if (!authToken) return;
    const gen = ++fetchGenRef.current;
    setLoading(true);
    setErr("");
    try {
      const data: RegistrationCode | null =
        await api.getRegistrationCodeCurrent(authToken);
      // 代次落后（doRefresh 已生成新码 / 已卸载）→ 丢弃这次迟到响应，不覆盖
      if (gen !== fetchGenRef.current) return;
      if (!data) {
        setCode(null);
        setExpiresAt(null);
        setCreatedAt(null);
      } else {
        setCode(data.code);
        setExpiresAt(new Date(data.expires_at).getTime());
        setCreatedAt(data.created_at);
      }
      setForbidden(false);
    } catch (e: any) {
      if (gen !== fetchGenRef.current) return;
      if (e && e.status === 403) {
        setForbidden(true);
      } else if (e && e.status) {
        setErr(`サーバーエラー (${e.status})`);
      } else {
        setErr("サーバーに接続できません");
      }
    } finally {
      if (gen === fetchGenRef.current) setLoading(false);
    }
  }, [authToken]);

  React.useEffect(() => {
    fetchCurrent();
    const id = setInterval(fetchCurrent, 30000);
    return () => {
      clearInterval(id);
      fetchGenRef.current++; // 卸载/重订阅时作废在飞请求，防已卸载 setState
    };
  }, [fetchCurrent]);

  const remainSec =
    expiresAt && now < expiresAt
      ? Math.max(0, Math.floor((expiresAt - now) / 1000))
      : 0;
  const mm = String(Math.floor(remainSec / 60)).padStart(2, "0");
  const ss = String(remainSec % 60).padStart(2, "0");
  const expired = expiresAt && now >= expiresAt;
  const locked = now < refreshLockUntil;

  const doRefresh = async () => {
    if (refreshing || locked) return;
    setRefreshing(true);
    setErr("");
    try {
      // 先作废在飞的旧轮询响应再发请求 — bump 放 await 之后的话，等待期间返回的
      // 旧轮询仍会短暂写回旧码（最终态虽对，界面会闪一下）
      fetchGenRef.current++;
      const data: RegistrationCode =
        await api.refreshRegistrationCode(authToken);
      // 写回前再 bump 一次 — 等待窗内新起飞的轮询（入口自取了更新代次）若慢返回
      // 且携带服务端未刷新的旧码，会盖掉下面写入的新码停留到下轮轮询；这里作废它
      fetchGenRef.current++;
      setCode(data.code);
      setExpiresAt(new Date(data.expires_at).getTime());
      setCreatedAt(data.created_at);
      setRefreshLockUntil(Date.now() + 10000); // 10 秒连按防抖（§11.9.1 拍板）
    } catch (e: any) {
      if (e && e.status === 403) setForbidden(true);
      else if (e && e.status) setErr(`サーバーエラー (${e.status})`);
      else setErr("サーバーに接続できません");
    } finally {
      setRefreshing(false);
      setConfirm(false);
    }
  };

  const doCopy = async () => {
    if (!code) return;
    try {
      await navigator.clipboard.writeText(code);
      setCopyToast(true);
      if (copyToastTimerRef.current != null) {
        clearTimeout(copyToastTimerRef.current);
      }
      copyToastTimerRef.current = setTimeout(() => {
        setCopyToast(false);
        copyToastTimerRef.current = null;
      }, 1500);
    } catch (e) {
      setErr("コピー失敗（手動で番号をコピーしてください）");
    }
  };

  if (forbidden) {
    return (
      <div style={{ padding: "28px 32px 48px" }}>
        <div
          style={{
            fontSize: 11,
            color: T.ink3,
            letterSpacing: 2,
            fontWeight: 600,
          }}
        >
          寮務 &gt; 寮生登録コード
        </div>
        <h1
          style={{
            fontSize: 24,
            fontWeight: 700,
            margin: "4px 0 20px",
            letterSpacing: -0.3,
          }}
        >
          403：権限がありません
        </h1>
        <div
          style={{
            padding: 18,
            background: T.dangerSoft,
            color: T.danger,
            border: `1px solid ${T.dangerBorder}`,
            borderRadius: 10,
            fontSize: 13,
            lineHeight: 1.7,
          }}
        >
          このページを表示する権限がありません。
        </div>
      </div>
    );
  }

  return (
    <div style={{ padding: "28px 32px 48px", maxWidth: 720 }}>
      <div
        style={{
          fontSize: 11,
          color: T.ink3,
          letterSpacing: 2,
          fontWeight: 600,
        }}
      >
        寮務 &gt; 寮生登録コード
      </div>
      <h1
        style={{
          fontSize: 24,
          fontWeight: 700,
          margin: "4px 0 6px",
          letterSpacing: -0.3,
        }}
      >
        寮生登録コード
      </h1>
      <div style={{ color: T.ink3, fontSize: 13, marginBottom: 22 }}>
        App Store 公開後の登録ゲート
      </div>

      {/* 当前注册码 block */}
      <div
        style={{
          background: T.surface,
          border: `1px solid ${T.line}`,
          borderRadius: 14,
          padding: "28px 24px",
          boxShadow: T.shadow1,
          marginBottom: 18,
        }}
      >
        <div
          style={{
            fontSize: 11,
            color: T.ink3,
            letterSpacing: 1.5,
            fontWeight: 600,
            marginBottom: 8,
          }}
        >
          現在のコード
        </div>
        {loading && !code ? (
          <div
            style={{
              fontSize: 14,
              color: T.ink3,
              padding: "20px 0",
              textAlign: "center",
            }}
          >
            読み込み中…
          </div>
        ) : !code ? (
          <div
            style={{
              fontSize: 14,
              color: T.ink3,
              padding: "20px 0",
              textAlign: "center",
            }}
          >
            有効なコードがありません —
            下の「新しいコードを生成」ボタンで作成してください
          </div>
        ) : (
          <>
            <div
              style={{
                fontFamily: T.mono,
                fontSize: 32,
                fontWeight: 700,
                letterSpacing: 6,
                textAlign: "center",
                padding: "12px 0",
                color: expired ? T.danger : T.ink,
              }}
            >
              {code.slice(0, 3)} {code.slice(3, 6)}
            </div>
            <div
              style={{
                textAlign: "center",
                fontSize: 12,
                fontFamily: T.mono,
                color: expired ? T.danger : T.ink2,
                marginBottom: 14,
              }}
            >
              {expired ? (
                <span style={{ fontWeight: 700 }}>
                  期限切れです。新しいコードを生成してください
                </span>
              ) : (
                <>
                  有効期限まで残り{" "}
                  <span style={{ fontWeight: 700 }}>
                    {mm}:{ss}
                  </span>
                </>
              )}
            </div>
            {createdAt && (
              <div
                style={{
                  fontSize: 11,
                  color: T.ink3,
                  textAlign: "center",
                  marginBottom: 14,
                }}
              >
                生成時刻:{" "}
                <span style={{ fontFamily: T.mono }}>
                  {new Date(createdAt).toLocaleString("ja-JP", {
                    timeZone: "Asia/Tokyo",
                  })}
                </span>
              </div>
            )}
          </>
        )}

        <div
          style={{
            display: "flex",
            gap: 10,
            justifyContent: "center",
            marginTop: 8,
          }}
        >
          <button
            onClick={() => setConfirm(true)}
            disabled={refreshing || locked}
            style={{
              padding: "10px 18px",
              background: refreshing || locked ? T.lineStrong : T.cobalt,
              color: "#fff",
              border: "none",
              borderRadius: 10,
              fontFamily: "inherit",
              fontSize: 13,
              fontWeight: 600,
              cursor: refreshing || locked ? "not-allowed" : "pointer",
            }}
          >
            {refreshing
              ? "生成中…"
              : locked
                ? `再生成可（${Math.ceil((refreshLockUntil - now) / 1000)}s）`
                : "新しいコードを生成"}
          </button>
          <button
            onClick={doCopy}
            disabled={!code}
            style={{
              padding: "10px 18px",
              background: T.surface,
              color: T.ink,
              border: `1px solid ${T.lineStrong}`,
              borderRadius: 10,
              fontFamily: "inherit",
              fontSize: 13,
              fontWeight: 600,
              cursor: code ? "pointer" : "not-allowed",
            }}
          >
            {copyToast ? "コピーしました ✓" : "コードをコピー"}
          </button>
        </div>
      </div>

      {err && (
        <div
          style={{
            padding: 12,
            background: T.dangerSoft,
            color: T.danger,
            border: `1px solid ${T.dangerBorder}`,
            borderRadius: 8,
            fontSize: 12,
            marginBottom: 14,
          }}
        >
          {err}
        </div>
      )}

      {/* 用法说明 block */}
      <div
        style={{
          background: T.surface,
          border: `1px solid ${T.line}`,
          borderRadius: 12,
          padding: "16px 20px",
          fontSize: 12,
          lineHeight: 1.9,
          color: T.ink2,
        }}
      >
        <div
          style={{
            fontWeight: 700,
            color: T.ink,
            marginBottom: 6,
            fontSize: 13,
          }}
        >
          使い方
        </div>
        <div>
          ① ボタンを押すと新しい 6
          桁コードが生成されます（前のコードは即座に無効になります）
        </div>
        <div>② 寮生にコードを伝達（口頭 / 黒板 / LINE）</div>
        <div>③ 寮生は登録手続きの最後の画面でコードを入力します</div>
        <div>④ コードは 5 分間有効です</div>
        <div>
          ⑤ 集団登録（新入生説明会など）では同じコードで複数人が登録できます
        </div>
      </div>

      {confirm && (
        <div
          onClick={() => setConfirm(false)}
          style={{
            position: "fixed",
            inset: 0,
            background: "rgba(20,23,31,.4)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            zIndex: 1000,
          }}
        >
          <div
            onClick={(e) => e.stopPropagation()}
            style={{
              background: T.surface,
              borderRadius: 14,
              padding: 24,
              width: 420,
              boxShadow: T.shadowModal,
            }}
          >
            <div style={{ fontSize: 16, fontWeight: 700, marginBottom: 8 }}>
              新しいコードを発行しますか?
            </div>
            <div
              style={{
                fontSize: 13,
                color: T.ink2,
                marginBottom: 18,
                lineHeight: 1.6,
              }}
            >
              現在のコードを<b>即座に無効化</b>
              して新しい 6 桁コードを発行します。 実行後 10
              秒間は再生成できません。
            </div>
            <div
              style={{
                display: "flex",
                gap: 10,
                justifyContent: "flex-end",
              }}
            >
              <button
                onClick={() => setConfirm(false)}
                style={{
                  padding: "8px 16px",
                  background: T.surface,
                  color: T.ink2,
                  border: `1px solid ${T.lineStrong}`,
                  borderRadius: 8,
                  fontFamily: "inherit",
                  fontSize: 13,
                  cursor: "pointer",
                }}
              >
                キャンセル
              </button>
              <button
                onClick={doRefresh}
                style={{
                  padding: "8px 16px",
                  background: T.cobalt,
                  color: "#fff",
                  border: "none",
                  borderRadius: 8,
                  fontFamily: "inherit",
                  fontSize: 13,
                  fontWeight: 700,
                  cursor: "pointer",
                }}
              >
                発行
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
