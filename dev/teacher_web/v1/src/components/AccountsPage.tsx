import React from "react";
import { RYO, type RyoTokens } from "../theme";
import { api } from "../api/client";
import { StudentProfileModal } from "./StudentProfileModal";
import type {
  TeacherProfile,
  StudentAccountListItem,
  RenewalStartOut,
  RenewalProgressOut,
  TeacherRenewSeatIn,
} from "../api/types";

// 源 index.html 24967-26830（accounts.jsx 块，只搬 AccountsPage + 私有子组件
// AcctStat / AccountDetailModal / Field / EditField + 私有助手 buildActivityMock）。
// 界面冻结：JSX 结构 + 内联 style 一字不改，仅改作用域引用
// （window.RYO→RYO / window.tomoshibiApi→api / window.StudentProfileModal→StudentProfileModal）。

// 轻提示气泡（成功绿 / 失败红）
type Toast = { type: "ok" | "err"; msg: string } | null;

// 一括進級（学年更新）modal 状态 — null=关闭 / {phase:"preview", preview} = 预览中
type PromoteModal = { phase: "preview"; preview: RenewalStartOut } | null;

// 临时密码一次性 modal
type TempPwModal = { name: string; student_no: string; pw: string } | null;

export function AccountsPage({
  teacher,
  authToken,
}: {
  teacher: TeacherProfile;
  authToken: string;
}) {
  const T = RYO;
  // accounts は後端から取得した StudentAccountListItem[] を保持する。
  // loading=true の間はスケルトン表示、error 時はエラーバナー表示。
  const [accounts, setAccounts] = React.useState<StudentAccountListItem[]>([]);
  const [loading, setLoading] = React.useState(true);
  const [loadError, setLoadError] = React.useState<string | null>(null);
  const [query, setQuery] = React.useState("");
  const [dormFilter, setDormFilter] = React.useState("all"); // all / 1 / 2 / 4 / locked
  const [detailTarget, setDetailTarget] =
    React.useState<StudentAccountListItem | null>(null);
  const [toast, setToast] = React.useState<Toast>(null);
  // 密码重置后把临时密码存这里，展示一次性 modal 后清空
  const [tempPwModal, setTempPwModal] = React.useState<TempPwModal>(null); // {name, student_no, pw}
  // 5-30: 个人档案聚合弹窗 — {id, name} | null
  const [profileTarget, setProfileTarget] = React.useState<{
    id: string;
    name: string;
  } | null>(null);
  // 6-05: 学年更新「开闸」modal — null=关闭 / {phase:"preview", preview} = 预览中
  // （推翻 5-30 老师代改进级 → 改成学生自设，老师只开闸 + 通知）
  const [promoteModal, setPromoteModal] = React.useState<PromoteModal>(null);
  const [promoteLoading, setPromoteLoading] = React.useState(false);
  const [promoteError, setPromoteError] = React.useState<string | null>(null);
  // 进度：还没自设番号的学生（needs_renewal=true）。{pending_count, items[]} | null
  const [renewalProgress, setRenewalProgress] =
    React.useState<RenewalProgressOut | null>(null);

  // 权限：仅寮務部長 / 寮務課長 / 管理係 可开闸 / 单件改番号
  const PROMOTE_ROLES = ["寮務部長", "寮務課長", "管理係"];
  const canPromote =
    teacher && teacher.role && PROMOTE_ROLES.includes(teacher.role);

  // 开闸（按钮「学年更新を開始」）：先 dry_run=true 预览（通知 N 人 + 毕业 M 人），确认后真执行
  const handlePromotePreview = () => {
    setPromoteError(null);
    setPromoteLoading(true);
    api
      .startRenewal({ dry_run: true }, authToken)
      .then((res) => {
        setPromoteModal({ phase: "preview", preview: res });
        setPromoteLoading(false);
      })
      .catch((e) => {
        setPromoteError(e.message || "プレビュー取得失敗");
        setPromoteLoading(false);
      });
  };

  const handlePromoteConfirm = () => {
    if (!promoteModal || !promoteModal.preview) return;
    setPromoteError(null);
    setPromoteLoading(true);
    api
      .startRenewal({ dry_run: false }, authToken)
      .then(() => {
        setPromoteModal(null);
        setPromoteLoading(false);
        setToast({ type: "ok", msg: "学年更新を開始しました" });
        fetchAccounts();
        fetchRenewalProgress();
      })
      .catch((e) => {
        setPromoteError(e.message || "学年更新の開始に失敗しました");
        setPromoteLoading(false);
      });
  };

  // 拉「谁还没自设番号」进度 — 进页面 + 开闸后刷新
  const fetchRenewalProgress = React.useCallback(() => {
    if (!authToken) return;
    api
      .renewalProgress(authToken)
      .then((res) => setRenewalProgress(res))
      .catch(() => setRenewalProgress(null));
  }, [authToken]);

  // 後端からリスト取得 — query / dormFilter が変わるたびに再取得
  const fetchAccounts = React.useCallback(() => {
    if (!authToken) return;
    setLoading(true);
    setLoadError(null);
    const params: { q?: string; dorm_unit?: number; status?: string } = {};
    if (query) params.q = query;
    // dormFilter が数字文字列 ("1"/"2"/"4") なら dorm_unit として渡す
    if (dormFilter === "locked") {
      params.status = "locked";
    } else if (dormFilter !== "all") {
      params.dorm_unit = Number(dormFilter);
    }
    api
      .listStudents(params, authToken)
      .then((res) => {
        setAccounts(res.items || []);
        setLoading(false);
      })
      .catch((e) => {
        setLoadError(e.message || "学生リストの取得に失敗しました");
        setLoading(false);
      });
  }, [authToken, query, dormFilter]);

  React.useEffect(() => {
    fetchAccounts();
  }, [fetchAccounts]);

  React.useEffect(() => {
    fetchRenewalProgress();
  }, [fetchRenewalProgress]);

  // 学生列表按「学年 → A/B 組」分组折叠（spec §4.2 做法 A）
  const [collapsedGroups, setCollapsedGroups] = React.useState<
    Record<string, boolean>
  >({});
  const GRADE_LABEL: Record<string, string> = {
    "01": "中1",
    "02": "中2",
    "03": "中3",
    "04": "高1",
    "05": "高2",
    "06": "高3",
  };
  const CLASS_LABEL: Record<string, string> = { "01": "A組", "02": "B組" };

  // フィルタ: locked だけ追加でフロント側絞り込み（後端 status=locked と二重になるが安全）
  let visible = accounts;
  if (dormFilter === "locked") visible = accounts.filter((a) => a.is_locked);
  // 後端検索済みなのでフロント側の追加テキスト絞り込みは不要

  // 按 学年码 → 组码 分组，组内保持后端给的 seat 顺序
  const gradeClassGroups = React.useMemo(() => {
    const map: Record<string, StudentAccountListItem[]> = {};
    visible.forEach((a) => {
      const key = `${a.grade_code || "??"}-${a.class_code || "??"}`;
      (map[key] = map[key] || []).push(a);
    });
    return Object.keys(map)
      .sort()
      .map((key) => {
        const [g, c] = key.split("-");
        return {
          key,
          label: `${GRADE_LABEL[g] || g} ${CLASS_LABEL[c] || c}`,
          rows: map[key],
        };
      });
  }, [visible]);

  const stats = {
    total: accounts.length,
    locked: accounts.filter((a) => a.is_locked).length,
  };

  const handleSave = (patch: { id: string; name: string; room_no: string }) => {
    // 編集可能項目（room_no 等）の保存は現在 backend 未実装 — フロント state のみ更新
    setAccounts((list) =>
      list.map((a) => (a.id === patch.id ? { ...a, ...patch } : a)),
    );
    setToast({
      type: "ok",
      msg: `${patch.name} のアカウントを更新しました`,
    });
    setDetailTarget(null);
  };

  // 密码重置 — 后端返回 temporary_password，只在前端内存显示一次
  const handlePasswordReset = (account: StudentAccountListItem) => {
    api
      .resetStudentPassword(account.id, authToken)
      .then((res) => {
        // 解锁后刷新该行 is_locked 状态
        setAccounts((list) =>
          list.map((a) =>
            a.id === account.id ? { ...a, is_locked: false } : a,
          ),
        );
        // 临时密码只存内存，弹一次性 modal 给老师看
        setTempPwModal({
          name: account.name,
          student_no: account.student_no,
          pw: res.temporary_password,
        });
        setDetailTarget(null);
      })
      .catch((e) => {
        setToast({
          type: "err",
          msg: `パスワードの初期化に失敗しました：${e.message || "エラー"}`,
        });
      });
  };

  // 老师单件改某学生番号（兜底 — 学生不会操作 / 填错时）。撞号后端返 422。
  const handleTeacherRenewSeat = (
    account: StudentAccountListItem,
    body: TeacherRenewSeatIn,
  ) => {
    api
      .teacherRenewSeat(account.id, body, authToken)
      .then(() => {
        setToast({ type: "ok", msg: "学籍番号を更新しました" });
        setDetailTarget(null);
        fetchAccounts();
        fetchRenewalProgress();
      })
      .catch((e) => {
        setToast({
          type: "err",
          msg: e.message || "学籍番号の更新に失敗しました",
        });
      });
  };

  // 解锁 — 成功后刷新该行 is_locked 状态
  const handleUnlock = (account: StudentAccountListItem) => {
    api
      .unlockStudentAccount(account.id, authToken)
      .then(() => {
        setAccounts((list) =>
          list.map((a) =>
            a.id === account.id ? { ...a, is_locked: false } : a,
          ),
        );
        setToast({
          type: "ok",
          msg: `${account.name} のロックを解除しました`,
        });
        setDetailTarget(null);
      })
      .catch((e) => {
        setToast({
          type: "err",
          msg: `ロック解除に失敗しました：${e.message || "エラー"}`,
        });
      });
  };

  React.useEffect(() => {
    if (toast) {
      const id = setTimeout(() => setToast(null), 4000);
      return () => clearTimeout(id);
    }
  }, [toast]);

  const nextNoHint = "06????"; // 番号 6 桁: 学年(2)+組(2)+番号(2)。iOS 登録時に学生本人入力

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
        学生管理
      </div>
      <div
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          flexWrap: "wrap",
          gap: 12,
          margin: "4px 0 20px",
        }}
      >
        <h1 style={{ fontSize: 24, fontWeight: 700, letterSpacing: -0.3 }}>
          学生アカウント管理
        </h1>
        <div style={{ display: "flex", gap: 8 }}>
          {canPromote && (
            <button
              onClick={handlePromotePreview}
              disabled={promoteLoading}
              style={{
                padding: "8px 14px",
                // 源用 T.amber || "#f59e0b"；theme.ts 无 amber 字段，运行时恒为 #f59e0b，保留同等行为
                background:
                  (T as RyoTokens & { amber?: string }).amber || "#f59e0b",
                color: "#fff",
                border: "none",
                borderRadius: 8,
                fontFamily: "inherit",
                fontSize: 13,
                fontWeight: 700,
                cursor: promoteLoading ? "not-allowed" : "pointer",
                opacity: promoteLoading ? 0.6 : 1,
              }}
            >
              {promoteLoading ? "読み込み中…" : "学年更新を開始"}
            </button>
          )}
          <button
            onClick={() =>
              alert(
                `新規登録は iOS App から本人入力（番号 = 学年 2 桁 + 組 2 桁 + 番号 2 桁、例：高 3 B 18 = 060218）。老師側追加未対応`,
              )
            }
            style={{
              padding: "8px 14px",
              background: "transparent",
              color: T.cobalt,
              border: `1px solid ${T.cobalt}`,
              borderRadius: 8,
              fontFamily: "inherit",
              fontSize: 13,
              fontWeight: 700,
              cursor: "pointer",
            }}
          >
            ＋ 新規追加
          </button>
          <button
            onClick={() => alert("CSV 出力 · 未対応")}
            style={{
              padding: "8px 14px",
              background: "transparent",
              color: T.ink3,
              border: `1px solid ${T.lineStrong}`,
              borderRadius: 8,
              fontFamily: "inherit",
              fontSize: 13,
              cursor: "pointer",
            }}
          >
            CSV 出力
          </button>
        </div>
      </div>

      {/* 一括進級 modal — dry_run=true 预览 → 确认 → dry_run=false 执行 */}
      {promoteModal && promoteModal.phase === "preview" && (
        <div
          style={{
            position: "fixed",
            inset: 0,
            background: "rgba(0,0,0,0.45)",
            zIndex: 1000,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
          }}
        >
          <div
            style={{
              background: T.surface,
              borderRadius: 12,
              padding: "28px 32px",
              width: 540,
              maxWidth: "90vw",
              maxHeight: "80vh",
              overflowY: "auto",
              boxShadow: "0 8px 32px rgba(0,0,0,0.18)",
            }}
          >
            <h2 style={{ fontSize: 18, fontWeight: 700, marginBottom: 8 }}>
              学年更新の開始（プレビュー）
            </h2>
            <p style={{ fontSize: 13, color: T.ink3, marginBottom: 16 }}>
              中1〜高2 に番号の再設定を依頼し、高3
              を卒業にします。学籍番号は学生本人が App
              で設定します。確認してから「実行」してください。
            </p>
            <div
              style={{
                display: "grid",
                gridTemplateColumns: "repeat(3,1fr)",
                gap: 8,
                marginBottom: 16,
              }}
            >
              {(
                [
                  ["通知", promoteModal.preview.notify_count, T.cobalt],
                  ["卒業", promoteModal.preview.graduate_count, T.ok],
                  ["合計", promoteModal.preview.total_affected, T.ink],
                ] as [string, number, string][]
              ).map(([label, val, color]) => (
                <div
                  key={label}
                  style={{
                    // 源用 T.surfaceAlt || T.bgStrong；theme.ts 无 bgStrong 字段，运行时恒为 surfaceAlt，保留同等行为
                    background:
                      T.surfaceAlt ||
                      (T as RyoTokens & { bgStrong?: string }).bgStrong,
                    borderRadius: 8,
                    padding: "10px 14px",
                    textAlign: "center",
                  }}
                >
                  <div style={{ fontSize: 11, color: T.ink3 }}>{label}</div>
                  <div
                    style={{
                      fontSize: 22,
                      fontWeight: 700,
                      color,
                    }}
                  >
                    {val}
                  </div>
                </div>
              ))}
            </div>
            <div
              style={{
                maxHeight: 240,
                overflowY: "auto",
                border: `1px solid ${T.lineStrong}`,
                borderRadius: 8,
                marginBottom: 16,
              }}
            >
              <table
                style={{
                  width: "100%",
                  fontSize: 12,
                  borderCollapse: "collapse",
                }}
              >
                <thead>
                  <tr
                    style={{
                      // 源用 T.bgStrong；theme.ts 无该字段，运行时为 undefined（=不设背景），保留同等行为
                      background: (T as RyoTokens & { bgStrong?: string })
                        .bgStrong,
                      position: "sticky",
                      top: 0,
                    }}
                  >
                    {["学番", "氏名", "学年", "対応"].map((h) => (
                      <th
                        key={h}
                        style={{
                          padding: "6px 10px",
                          textAlign: "left",
                          fontWeight: 600,
                          color: T.ink3,
                        }}
                      >
                        {h}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {promoteModal.preview.entries.map((e) => (
                    <tr
                      key={e.student_id}
                      style={{
                        borderTop: `1px solid ${T.line}`,
                      }}
                    >
                      <td style={{ padding: "5px 10px", color: T.ink3 }}>
                        {e.student_no}
                      </td>
                      <td style={{ padding: "5px 10px" }}>{e.name}</td>
                      <td style={{ padding: "5px 10px", color: T.ink3 }}>
                        {GRADE_LABEL[e.grade_code] || e.grade_code}
                      </td>
                      <td
                        style={{
                          padding: "5px 10px",
                          color: e.action === "graduate" ? T.ok : T.cobalt,
                          fontWeight: 600,
                        }}
                      >
                        {e.action === "graduate" ? "卒業" : "番号再設定を依頼"}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            {promoteError && (
              <div
                style={{
                  padding: "8px 12px",
                  background: T.dangerSoft,
                  color: T.danger,
                  borderRadius: 6,
                  fontSize: 13,
                  marginBottom: 12,
                }}
              >
                ⚠️ {promoteError}
              </div>
            )}
            <div
              style={{
                display: "flex",
                gap: 8,
                justifyContent: "flex-end",
              }}
            >
              <button
                onClick={() => {
                  setPromoteModal(null);
                  setPromoteError(null);
                }}
                style={{
                  padding: "8px 18px",
                  background: "transparent",
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
                onClick={handlePromoteConfirm}
                disabled={promoteLoading}
                style={{
                  padding: "8px 18px",
                  background: T.danger,
                  color: "#fff",
                  border: "none",
                  borderRadius: 8,
                  fontFamily: "inherit",
                  fontSize: 13,
                  fontWeight: 700,
                  cursor: promoteLoading ? "not-allowed" : "pointer",
                  opacity: promoteLoading ? 0.6 : 1,
                }}
              >
                {promoteLoading ? "実行中…" : "実行する"}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* エラーバナー — 後端取得失敗時 */}
      {loadError && (
        <div
          style={{
            padding: "10px 14px",
            background: T.dangerSoft,
            border: `1px solid ${T.dangerBorder}`,
            borderRadius: 8,
            color: T.danger,
            fontSize: 13,
            marginBottom: 16,
          }}
        >
          ⚠️ {loadError}
        </div>
      )}

      {/* 学年更新进度横幅 — 有人待自设番号时显示（各组人数在下面列表组标题里）*/}
      {renewalProgress && renewalProgress.pending_count > 0 && (
        <div
          style={{
            padding: "10px 14px",
            background: T.warnSoft,
            border: `1px solid ${T.warnBorder}`,
            borderRadius: 8,
            color: T.warn,
            fontSize: 13,
            fontWeight: 600,
            marginBottom: 16,
          }}
        >
          学年更新：未更新 {renewalProgress.pending_count} 名 —
          各組見出しに内訳を表示
        </div>
      )}

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(3, 1fr)",
          gap: 12,
          marginBottom: 20,
        }}
      >
        <AcctStat
          label="総アカウント"
          value={loading ? "…" : stats.total}
          note="サーバーから取得"
          color={T.ink}
        />
        <AcctStat
          label="ロック中"
          value={loading ? "…" : stats.locked}
          note={stats.locked > 0 ? "要対応" : "異常無し"}
          color={stats.locked > 0 ? T.danger : T.ok}
          onClick={stats.locked > 0 ? () => setDormFilter("locked") : null}
        />
        <AcctStat
          label="番号フォーマット"
          value={nextNoHint}
          note="学年+組+番号 6 桁"
          color={T.ink3}
          mono
        />
      </div>

      <div
        style={{
          display: "flex",
          gap: 10,
          alignItems: "center",
          marginBottom: 14,
          flexWrap: "wrap",
        }}
      >
        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="番号・氏名で検索"
          style={{
            flex: 1,
            minWidth: 280,
            padding: "10px 14px",
            background: T.surface,
            border: `1px solid ${T.lineStrong}`,
            borderRadius: 10,
            fontFamily: "inherit",
            fontSize: 13,
            outline: "none",
            boxSizing: "border-box",
          }}
        />
        <div
          style={{
            display: "flex",
            gap: 4,
            background: T.surface,
            border: `1px solid ${T.lineStrong}`,
            borderRadius: 999,
            padding: 3,
          }}
        >
          {[
            ["all", "全員"],
            ["1", "1寮"],
            ["2", "2寮"],
            ["4", "4寮"],
            ["locked", "ロック中"],
          ].map(([k, l]) => (
            <button
              key={k}
              onClick={() => setDormFilter(k)}
              style={{
                padding: "5px 14px",
                background: dormFilter === k ? T.cobalt : "transparent",
                color: dormFilter === k ? "#fff" : T.ink2,
                border: "none",
                borderRadius: 999,
                fontFamily: "inherit",
                fontSize: 12,
                fontWeight: 600,
                cursor: "pointer",
              }}
            >
              {l}
            </button>
          ))}
        </div>
      </div>

      <div
        style={{
          background: T.surface,
          border: `1px solid ${T.line}`,
          borderRadius: 12,
          overflow: "hidden",
          boxShadow: T.shadow1,
        }}
      >
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "110px 160px 80px 60px 80px 130px 110px 90px",
            background: T.surfaceAlt,
            fontSize: 11,
            color: T.ink2,
            fontWeight: 600,
            letterSpacing: 1,
            borderBottom: `1px solid ${T.line}`,
          }}
        >
          {[
            "学籍番号",
            "氏名",
            "部屋",
            "寮",
            "性別",
            "最終ログイン",
            "状態",
            "",
          ].map((h) => (
            <div key={h} style={{ padding: "10px 12px" }}>
              {h}
            </div>
          ))}
        </div>
        {loading && (
          <div
            style={{
              padding: 40,
              textAlign: "center",
              color: T.ink3,
              fontSize: 13,
            }}
          >
            読み込み中…
          </div>
        )}
        {!loading &&
          gradeClassGroups.map((group) => {
            const isCollapsed = collapsedGroups[group.key];
            const groupPending = group.rows.filter(
              (r) => r.needs_renewal,
            ).length;
            return (
              <React.Fragment key={group.key}>
                {/* 分组标题行（学年+组）点击折叠，右侧显示人数 + 未更新数 */}
                <div
                  onClick={() =>
                    setCollapsedGroups((m) => ({
                      ...m,
                      [group.key]: !m[group.key],
                    }))
                  }
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: 8,
                    padding: "8px 12px",
                    background: T.surfaceAlt,
                    borderTop: `1px solid ${T.line}`,
                    cursor: "pointer",
                    fontSize: 12,
                    fontWeight: 700,
                    color: T.ink2,
                  }}
                >
                  <span style={{ color: T.ink3 }}>
                    {isCollapsed ? "▶" : "▼"}
                  </span>
                  <span>{group.label}</span>
                  <span style={{ color: T.ink3, fontWeight: 500 }}>
                    · {group.rows.length}人
                  </span>
                  {groupPending > 0 && (
                    <span
                      style={{
                        fontSize: 11,
                        fontWeight: 700,
                        padding: "1px 8px",
                        borderRadius: 8,
                        background: T.warnSoft,
                        color: T.warn,
                      }}
                    >
                      未更新 {groupPending}
                    </span>
                  )}
                </div>
                {!isCollapsed &&
                  group.rows.map((a, i) => (
                    <div
                      key={a.id}
                      onClick={() => setDetailTarget(a)}
                      style={{
                        display: "grid",
                        gridTemplateColumns:
                          "110px 160px 80px 60px 80px 130px 110px 90px",
                        borderTop: i > 0 ? `1px solid ${T.line}` : "none",
                        fontSize: 12.5,
                        alignItems: "center",
                        cursor: "pointer",
                        transition: "background .1s",
                      }}
                      onMouseEnter={(e) =>
                        (e.currentTarget.style.background = T.surfaceAlt)
                      }
                      onMouseLeave={(e) =>
                        (e.currentTarget.style.background = "transparent")
                      }
                    >
                      <div
                        style={{
                          padding: "10px 12px",
                          fontFamily: T.mono,
                          fontWeight: 700,
                          color: T.ink2,
                        }}
                      >
                        {a.student_no}
                      </div>
                      <div style={{ padding: "10px 12px", fontWeight: 600 }}>
                        {a.name}
                      </div>
                      <div
                        style={{
                          padding: "10px 12px",
                          fontFamily: T.mono,
                          color: T.ink3,
                        }}
                      >
                        {a.room_no}
                      </div>
                      <div
                        style={{
                          padding: "10px 12px",
                          fontFamily: T.mono,
                          color: T.ink3,
                        }}
                      >
                        {a.dorm_unit}寮
                      </div>
                      <div style={{ padding: "10px 12px", color: T.ink3 }}>
                        {a.gender === "male" ? "男" : "女"}
                      </div>
                      <div
                        style={{
                          padding: "10px 12px",
                          fontFamily: T.mono,
                          fontSize: 11,
                          color: T.ink3,
                        }}
                      >
                        {a.last_login_at ? a.last_login_at.slice(5, 16) : "—"}
                      </div>
                      <div style={{ padding: "10px 12px" }}>
                        {a.is_locked ? (
                          <span
                            style={{
                              fontSize: 11,
                              fontWeight: 700,
                              padding: "2px 8px",
                              borderRadius: 4,
                              background: T.dangerSoft,
                              color: T.danger,
                              border: `1px solid ${T.dangerBorder}`,
                            }}
                          >
                            🔒 ロック
                          </span>
                        ) : a.status === "active" ? (
                          <span
                            style={{
                              fontSize: 11,
                              fontWeight: 700,
                              padding: "2px 8px",
                              borderRadius: 4,
                              background: T.okSoft,
                              color: T.ok,
                              border: `1px solid ${T.okBorder}`,
                            }}
                          >
                            正常
                          </span>
                        ) : (
                          <span
                            style={{
                              fontSize: 11,
                              fontWeight: 700,
                              padding: "2px 8px",
                              borderRadius: 4,
                              background: T.warnSoft,
                              color: T.warn,
                              border: `1px solid ${T.warnBorder}`,
                            }}
                          >
                            {a.status}
                          </span>
                        )}
                      </div>
                      <div
                        style={{
                          padding: "6px 8px",
                          display: "flex",
                          gap: 4,
                          alignItems: "center",
                        }}
                      >
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            setDetailTarget(a);
                          }}
                          style={{
                            padding: "4px 9px",
                            fontSize: 11,
                            fontWeight: 700,
                            background: "transparent",
                            color: T.cobalt,
                            border: `1px solid ${T.cobalt}`,
                            borderRadius: 6,
                            cursor: "pointer",
                            fontFamily: "inherit",
                          }}
                        >
                          詳細
                        </button>
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            setProfileTarget({ id: a.id, name: a.name });
                          }}
                          style={{
                            padding: "4px 9px",
                            fontSize: 11,
                            fontWeight: 700,
                            background: "transparent",
                            color: T.ink2,
                            border: `1px solid ${T.lineStrong}`,
                            borderRadius: 6,
                            cursor: "pointer",
                            fontFamily: "inherit",
                          }}
                        >
                          記録
                        </button>
                      </div>
                    </div>
                  ))}
              </React.Fragment>
            );
          })}
        {!loading && visible.length === 0 && (
          <div
            style={{
              padding: 40,
              textAlign: "center",
              color: T.ink3,
              fontSize: 13,
            }}
          >
            該当するアカウントがありません
          </div>
        )}
      </div>

      {detailTarget && (
        <AccountDetailModal
          account={detailTarget}
          onClose={() => setDetailTarget(null)}
          onSave={handleSave}
          onPasswordReset={handlePasswordReset}
          onUnlock={handleUnlock}
          onRenewSeat={handleTeacherRenewSeat}
        />
      )}

      {/* 5-30: 个人档案聚合弹窗 */}
      {profileTarget && (
        <StudentProfileModal
          studentId={profileTarget.id}
          studentName={profileTarget.name}
          authToken={authToken}
          onClose={() => setProfileTarget(null)}
        />
      )}

      {/* 臨時パスワード一回限り表示 modal — 閉じたら消える */}
      {tempPwModal && (
        <div
          onClick={() => setTempPwModal(null)}
          style={{
            position: "fixed",
            inset: 0,
            background: "rgba(20,23,31,.55)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            zIndex: 200,
            fontFamily: T.font,
          }}
        >
          <div
            onClick={(e) => e.stopPropagation()}
            style={{
              width: 420,
              background: T.surface,
              borderRadius: 14,
              boxShadow: T.shadowModal,
              padding: "28px 28px 20px",
            }}
          >
            <div
              style={{
                fontSize: 16,
                fontWeight: 700,
                marginBottom: 6,
              }}
            >
              🔑 仮パスワード発行
            </div>
            <div
              style={{
                fontSize: 13,
                color: T.ink2,
                marginBottom: 16,
                lineHeight: 1.7,
              }}
            >
              {tempPwModal.name}（{tempPwModal.student_no}）
              <br />
              以下の仮パスワードを本人に直接伝えてください。
              <br />
              <b>この画面を閉じると二度と表示されません。</b>
            </div>
            <div
              style={{
                display: "flex",
                alignItems: "center",
                gap: 8,
                background: T.surfaceAlt,
                border: `1px solid ${T.lineStrong}`,
                borderRadius: 8,
                padding: "10px 14px",
                marginBottom: 20,
              }}
            >
              <code
                style={{
                  flex: 1,
                  fontFamily: T.mono,
                  fontSize: 18,
                  fontWeight: 700,
                  letterSpacing: 2,
                  color: T.ink,
                }}
              >
                {tempPwModal.pw}
              </code>
              <button
                onClick={() =>
                  navigator.clipboard
                    .writeText(tempPwModal.pw)
                    .then(() => setToast({ type: "ok", msg: "コピーしました" }))
                }
                style={{
                  padding: "5px 12px",
                  background: T.cobalt,
                  color: "#fff",
                  border: "none",
                  borderRadius: 6,
                  fontFamily: "inherit",
                  fontSize: 12,
                  fontWeight: 700,
                  cursor: "pointer",
                }}
              >
                コピー
              </button>
            </div>
            <div style={{ display: "flex", justifyContent: "flex-end" }}>
              <button
                onClick={() => setTempPwModal(null)}
                style={{
                  padding: "8px 20px",
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
                確認・閉じる
              </button>
            </div>
          </div>
        </div>
      )}

      {toast && (
        <div
          style={{
            position: "fixed",
            bottom: 24,
            left: "50%",
            transform: "translateX(-50%)",
            background: toast.type === "ok" ? T.okSoft : T.dangerSoft,
            color: toast.type === "ok" ? T.ok : T.danger,
            border: `1px solid ${toast.type === "ok" ? T.okBorder : T.dangerBorder}`,
            padding: "10px 18px",
            borderRadius: 999,
            fontSize: 13,
            fontWeight: 600,
            zIndex: 1000,
            boxShadow: T.shadow2,
            maxWidth: 600,
          }}
        >
          {toast.msg}
        </div>
      )}
    </div>
  );
}

function AcctStat({
  label,
  value,
  note,
  color,
  onClick,
  mono,
}: {
  label: string;
  value: React.ReactNode;
  note: React.ReactNode;
  color: string;
  onClick?: (() => void) | null;
  mono?: boolean;
}) {
  const T = RYO;
  return (
    <div
      onClick={onClick || undefined}
      style={{
        padding: "14px 16px",
        background: T.surface,
        border: `1px solid ${T.line}`,
        borderRadius: 10,
        cursor: onClick ? "pointer" : "default",
      }}
    >
      <div
        style={{
          fontSize: 10,
          color: T.ink3,
          letterSpacing: 1.5,
          fontWeight: 600,
        }}
      >
        {label}
      </div>
      <div
        style={{
          fontSize: 26,
          fontWeight: 700,
          color,
          fontFamily: mono ? T.mono : "inherit",
          margin: "4px 0",
        }}
      >
        {value}
      </div>
      <div style={{ fontSize: 11, color: T.ink3 }}>{note}</div>
    </div>
  );
}

function AccountDetailModal({
  account,
  onClose,
  onSave,
  onPasswordReset,
  onUnlock,
  onRenewSeat,
}: {
  account: StudentAccountListItem;
  onClose: () => void;
  onSave: (patch: { id: string; name: string; room_no: string }) => void;
  onPasswordReset: (account: StudentAccountListItem) => void;
  onUnlock: (account: StudentAccountListItem) => void;
  onRenewSeat: (
    account: StudentAccountListItem,
    body: TeacherRenewSeatIn,
  ) => void;
}) {
  const T = RYO;
  const [tab, setTab] = React.useState("profile");
  // 後端の StudentAccountListItem には email / phone がないため空文字で初期化
  const [room, setRoom] = React.useState(account.room_no || "");
  const dirty = room !== (account.room_no || "");
  // 学籍番号 单件改（兜底）— 学年/组/出席番号 三选择，预填当前值
  const [rnGrade, setRnGrade] = React.useState(account.grade_code || "");
  const [rnClass, setRnClass] = React.useState(account.class_code || "");
  const [rnSeat, setRnSeat] = React.useState(account.seat_no || "");
  const rnDirty =
    rnGrade !== account.grade_code ||
    rnClass !== account.class_code ||
    rnSeat !== account.seat_no;
  const rnValid =
    /^0[1-6]$/.test(rnGrade) &&
    /^0[12]$/.test(rnClass) &&
    /^\d{2}$/.test(rnSeat);

  const genderLabel = { male: "男性", female: "女性" }[account.gender] || "—";

  // アクティビティ履歴 — 後端 API 未実装につきモック
  const activities = buildActivityMock(account);

  return (
    <div
      onClick={onClose}
      style={{
        position: "fixed",
        inset: 0,
        background: "rgba(20,23,31,.55)",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        zIndex: 100,
        fontFamily: T.font,
        padding: 20,
      }}
    >
      <div
        onClick={(e) => e.stopPropagation()}
        style={{
          width: 820,
          maxHeight: "94vh",
          overflow: "auto",
          background: T.surface,
          borderRadius: 14,
          boxShadow: T.shadowModal,
          color: T.ink,
        }}
      >
        <div
          style={{
            padding: "20px 28px 16px",
            borderBottom: `1px solid ${T.line}`,
            background: T.surfaceAlt,
            borderRadius: "14px 14px 0 0",
            display: "flex",
            alignItems: "center",
            gap: 16,
          }}
        >
          <div
            style={{
              width: 56,
              height: 56,
              borderRadius: 28,
              background: T.cobaltSoft,
              color: T.cobaltDeep,
              fontSize: 22,
              fontWeight: 700,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
            }}
          >
            {account.name.charAt(0)}
          </div>
          <div style={{ flex: 1 }}>
            <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
              <span
                style={{
                  fontFamily: T.mono,
                  fontSize: 14,
                  color: T.ink3,
                  fontWeight: 700,
                }}
              >
                学籍番号 {account.student_no}
              </span>
              {account.is_locked && (
                <span
                  style={{
                    fontSize: 10,
                    padding: "2px 8px",
                    background: T.danger,
                    color: "#fff",
                    borderRadius: 4,
                    fontWeight: 700,
                    letterSpacing: 1,
                  }}
                >
                  🔒 ロック中
                </span>
              )}
            </div>
            <div
              style={{
                fontSize: 22,
                fontWeight: 700,
                letterSpacing: -0.3,
                marginTop: 2,
              }}
            >
              {account.name}
            </div>
            <div style={{ fontSize: 12, color: T.ink3, marginTop: 2 }}>
              部屋 {account.room_no} · {account.dorm_unit}寮 · {genderLabel}
            </div>
          </div>
          <button
            onClick={onClose}
            style={{
              background: "transparent",
              border: "none",
              fontSize: 22,
              color: T.ink3,
              cursor: "pointer",
            }}
          >
            ×
          </button>
        </div>

        <div
          style={{
            display: "flex",
            gap: 4,
            padding: "0 28px",
            borderBottom: `1px solid ${T.line}`,
          }}
        >
          {[
            ["profile", "プロフィール・設定"],
            ["activity", "アクティビティ履歴"],
          ].map(([k, l]) => (
            <button
              key={k}
              onClick={() => setTab(k)}
              style={{
                padding: "12px 18px",
                background: "transparent",
                border: "none",
                borderBottom:
                  tab === k ? `2px solid ${T.cobalt}` : "2px solid transparent",
                color: tab === k ? T.cobaltDeep : T.ink3,
                fontWeight: tab === k ? 700 : 500,
                fontFamily: "inherit",
                fontSize: 13,
                cursor: "pointer",
                marginBottom: -1,
              }}
            >
              {l}
            </button>
          ))}
        </div>

        {tab === "profile" && (
          <div style={{ padding: "22px 28px" }}>
            <div
              style={{
                fontSize: 11,
                color: T.ink3,
                letterSpacing: 2,
                fontWeight: 700,
                marginBottom: 10,
                paddingBottom: 6,
                borderBottom: `1px solid ${T.line}`,
              }}
            >
              § 基本情報（編集不可 · 登録時に確定）
            </div>
            <div
              style={{
                display: "grid",
                gridTemplateColumns: "1fr 1fr",
                gap: "10px 20px",
                marginBottom: 24,
              }}
            >
              <Field label="学籍番号" mono>
                {account.student_no}
              </Field>
              <Field label="氏名">{account.name}</Field>
              <Field label="性別">{genderLabel}</Field>
              <Field label="部屋番号" mono>
                {account.room_no}
              </Field>
              <Field label="寮棟">{account.dorm_unit}寮</Field>
              <Field label="ステータス" mono>
                {account.status}
              </Field>
              <Field label="最終ログイン" mono>
                {account.last_login_at
                  ? account.last_login_at.slice(0, 16)
                  : "未ログイン"}
              </Field>
            </div>

            <div
              style={{
                fontSize: 11,
                color: T.ink3,
                letterSpacing: 2,
                fontWeight: 700,
                marginBottom: 10,
                paddingBottom: 6,
                borderBottom: `1px solid ${T.line}`,
              }}
            >
              § 編集可能項目
            </div>
            <div
              style={{
                display: "grid",
                gridTemplateColumns: "1fr 1fr",
                gap: "12px 20px",
                marginBottom: 24,
              }}
            >
              <EditField
                label="部屋番号"
                value={room}
                onChange={setRoom}
                mono
              />
              <div />
            </div>

            {/* 学籍番号 单件改（兜底）— 通常学生自设，老师在此替不会操作 / 填错的学生改 */}
            <div
              style={{
                fontSize: 11,
                color: T.ink3,
                letterSpacing: 2,
                fontWeight: 700,
                marginBottom: 10,
                paddingBottom: 6,
                borderBottom: `1px solid ${T.line}`,
              }}
            >
              § 学籍番号（学年更新の補助）
            </div>
            <div style={{ marginBottom: 24 }}>
              <div
                style={{
                  display: "flex",
                  gap: 10,
                  alignItems: "flex-end",
                  flexWrap: "wrap",
                }}
              >
                <label style={{ fontSize: 12, color: T.ink3 }}>
                  学年
                  <select
                    value={rnGrade}
                    onChange={(e) => setRnGrade(e.target.value)}
                    style={{
                      display: "block",
                      marginTop: 4,
                      padding: "6px 8px",
                      borderRadius: 6,
                      border: `1px solid ${T.lineStrong}`,
                      fontFamily: "inherit",
                      fontSize: 13,
                    }}
                  >
                    <option value="01">中1</option>
                    <option value="02">中2</option>
                    <option value="03">中3</option>
                    <option value="04">高1</option>
                    <option value="05">高2</option>
                    <option value="06">高3</option>
                  </select>
                </label>
                <label style={{ fontSize: 12, color: T.ink3 }}>
                  組
                  <select
                    value={rnClass}
                    onChange={(e) => setRnClass(e.target.value)}
                    style={{
                      display: "block",
                      marginTop: 4,
                      padding: "6px 8px",
                      borderRadius: 6,
                      border: `1px solid ${T.lineStrong}`,
                      fontFamily: "inherit",
                      fontSize: 13,
                    }}
                  >
                    <option value="01">A組</option>
                    <option value="02">B組</option>
                  </select>
                </label>
                <label style={{ fontSize: 12, color: T.ink3 }}>
                  出席番号
                  <input
                    value={rnSeat}
                    onChange={(e) =>
                      setRnSeat(e.target.value.replace(/\D/g, "").slice(0, 2))
                    }
                    placeholder="18"
                    style={{
                      display: "block",
                      marginTop: 4,
                      padding: "6px 8px",
                      width: 60,
                      borderRadius: 6,
                      border: `1px solid ${T.lineStrong}`,
                      fontFamily: T.mono,
                      fontSize: 13,
                    }}
                  />
                </label>
                <button
                  disabled={!rnDirty || !rnValid}
                  onClick={() =>
                    onRenewSeat &&
                    onRenewSeat(account, {
                      grade_code: rnGrade,
                      class_code: rnClass,
                      seat_no: rnSeat,
                    })
                  }
                  style={{
                    padding: "8px 14px",
                    background: !rnDirty || !rnValid ? T.lineStrong : T.cobalt,
                    color: "#fff",
                    border: "none",
                    borderRadius: 8,
                    fontFamily: "inherit",
                    fontSize: 13,
                    fontWeight: 700,
                    cursor: !rnDirty || !rnValid ? "not-allowed" : "pointer",
                  }}
                >
                  番号を更新 → {rnGrade}
                  {rnClass}
                  {rnSeat}
                </button>
              </div>
              <div style={{ fontSize: 11, color: T.ink3, marginTop: 6 }}>
                ※ 通常は学生本人が App
                で設定します。本人ができない・誤入力時の補助です。
              </div>
            </div>

            <div
              style={{
                fontSize: 11,
                color: T.ink3,
                letterSpacing: 2,
                fontWeight: 700,
                marginBottom: 10,
                paddingBottom: 6,
                borderBottom: `1px solid ${T.line}`,
              }}
            >
              § パスワード・セキュリティ
            </div>
            <div
              style={{
                background: T.warnSoft,
                border: `1px solid ${T.warnBorder}`,
                borderRadius: 8,
                padding: "12px 14px",
                marginBottom: 12,
                fontSize: 12,
                color: T.warn,
                lineHeight: 1.7,
              }}
            >
              ⚠️ パスワードは iOS App
              内で変更できません。本人がロックされた・忘れた場合は、下のボタンで仮パスワードを発行してください（本人に直接伝達）。
            </div>
            <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
              <button
                onClick={() => {
                  if (
                    confirm(
                      `${account.name}（${account.student_no}）のパスワードを初期化し、仮パスワードを発行しますか？`,
                    )
                  )
                    onPasswordReset(account);
                }}
                style={{
                  padding: "9px 18px",
                  background: T.warn,
                  color: "#fff",
                  border: "none",
                  borderRadius: 8,
                  fontFamily: "inherit",
                  fontSize: 13,
                  fontWeight: 700,
                  cursor: "pointer",
                }}
              >
                🔑 パスワード初期化・仮発行
              </button>
              {account.is_locked && (
                <button
                  onClick={() => {
                    if (
                      confirm(
                        `${account.name}（${account.student_no}）のロックを解除しますか？`,
                      )
                    )
                      onUnlock(account);
                  }}
                  style={{
                    padding: "9px 18px",
                    background: T.danger,
                    color: "#fff",
                    border: "none",
                    borderRadius: 8,
                    fontFamily: "inherit",
                    fontSize: 13,
                    fontWeight: 700,
                    cursor: "pointer",
                  }}
                >
                  🔓 ロック解除
                </button>
              )}
              <button
                onClick={() =>
                  alert("アカウント無効化 · 未対応（卒業・退寮時に使用）")
                }
                style={{
                  padding: "9px 18px",
                  background: "transparent",
                  color: T.ink3,
                  border: `1px solid ${T.lineStrong}`,
                  borderRadius: 8,
                  fontFamily: "inherit",
                  fontSize: 13,
                  cursor: "pointer",
                }}
              >
                アカウント無効化
              </button>
            </div>
          </div>
        )}

        {tab === "activity" && (
          <div style={{ padding: "22px 28px" }}>
            <div
              style={{
                fontSize: 11,
                color: T.ink3,
                letterSpacing: 2,
                fontWeight: 700,
                marginBottom: 12,
              }}
            >
              § この学生の最近のアクティビティ
            </div>
            <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
              {activities.map((act, i) => (
                <div
                  key={i}
                  style={{
                    display: "flex",
                    gap: 12,
                    padding: "12px 14px",
                    background: T.surface,
                    border: `1px solid ${T.line}`,
                    borderRadius: 10,
                  }}
                >
                  <div
                    style={{
                      width: 28,
                      height: 28,
                      borderRadius: 14,
                      background: act.color + "1a",
                      color: act.color,
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                      fontSize: 13,
                      flexShrink: 0,
                    }}
                  >
                    {act.icon}
                  </div>
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <div
                      style={{
                        fontSize: 13,
                        fontWeight: 600,
                        color: T.ink,
                      }}
                    >
                      {act.title}
                    </div>
                    <div
                      style={{
                        fontSize: 12,
                        color: T.ink2,
                        marginTop: 2,
                      }}
                    >
                      {act.body}
                    </div>
                  </div>
                  <div
                    style={{
                      fontSize: 11,
                      color: T.ink3,
                      fontFamily: T.mono,
                      whiteSpace: "nowrap",
                    }}
                  >
                    {act.when}
                  </div>
                </div>
              ))}
            </div>
            <div
              style={{
                marginTop: 16,
                fontSize: 11,
                color: T.ink3,
                textAlign: "center",
              }}
            >
              過去 30 日分表示 ·
              全履歴は「点呼記録」「減点・処分」「申請」で個別に確認できます
            </div>
          </div>
        )}

        <div
          style={{
            padding: "14px 28px",
            borderTop: `1px solid ${T.line}`,
            background: T.surfaceAlt,
            display: "flex",
            justifyContent: "flex-end",
            gap: 8,
            borderRadius: "0 0 14px 14px",
          }}
        >
          <button
            onClick={onClose}
            style={{
              padding: "9px 18px",
              background: "transparent",
              color: T.ink,
              border: `1px solid ${T.lineStrong}`,
              borderRadius: 8,
              fontFamily: "inherit",
              fontSize: 13,
              fontWeight: 600,
              cursor: "pointer",
            }}
          >
            閉じる
          </button>
          {tab === "profile" && (
            <button
              disabled={!dirty}
              onClick={() =>
                onSave({
                  id: account.id,
                  name: account.name,
                  room_no: room,
                })
              }
              style={{
                padding: "9px 20px",
                background: dirty ? T.cobalt : T.lineStrong,
                color: "#fff",
                border: "none",
                borderRadius: 8,
                fontFamily: "inherit",
                fontSize: 13,
                fontWeight: 700,
                cursor: dirty ? "pointer" : "not-allowed",
              }}
            >
              保存
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

function Field({
  label,
  children,
  mono,
}: {
  label: React.ReactNode;
  children: React.ReactNode;
  mono?: boolean;
}) {
  const T = RYO;
  return (
    <div>
      <div
        style={{
          fontSize: 10,
          color: T.ink3,
          fontWeight: 600,
          letterSpacing: 1,
          marginBottom: 3,
        }}
      >
        {label}
      </div>
      <div
        style={{
          fontSize: 13,
          color: T.ink,
          fontFamily: mono ? T.mono : "inherit",
        }}
      >
        {children}
      </div>
    </div>
  );
}

function EditField({
  label,
  value,
  onChange,
  type = "text",
  mono,
}: {
  label: React.ReactNode;
  value: string;
  onChange: (v: string) => void;
  type?: string;
  mono?: boolean;
}) {
  const T = RYO;
  return (
    <div>
      <div
        style={{
          fontSize: 10,
          color: T.ink3,
          fontWeight: 600,
          letterSpacing: 1,
          marginBottom: 5,
        }}
      >
        {label}
      </div>
      <input
        type={type}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        style={{
          width: "100%",
          padding: "8px 10px",
          background: T.surface,
          border: `1px solid ${T.lineStrong}`,
          borderRadius: 6,
          fontFamily: mono ? T.mono : "inherit",
          fontSize: 13,
          color: T.ink,
          outline: "none",
          boxSizing: "border-box",
        }}
      />
    </div>
  );
}

// アクティビティ履歴は後端 API 未実装 — 後端の last_login_at だけ使い、残りはモック表示。
function buildActivityMock(a: StudentAccountListItem) {
  const T = RYO;
  const loginWhen = a.last_login_at ? a.last_login_at.slice(5, 16) : "—";
  // 一条履歴的形：图标 / 颜色 / 标题 / 正文 / 时间 — 显式标类型避免数组被推断成两种固定颜色的联合
  type Activity = {
    icon: string;
    color: string;
    title: string;
    body: string;
    when: string;
  };
  const base: Activity[] = [
    {
      icon: "✓",
      color: T.ok,
      title: "点呼チェックイン",
      body: "夜点呼 · 時間内 · NFC カード",
      when: "04-22 19:30",
    },
    {
      icon: "📋",
      color: T.cobalt,
      title: "ログイン",
      body: "iOS App",
      when: loginWhen,
    },
  ];
  if (a.is_locked)
    base.push({
      icon: "🔒",
      color: T.danger,
      title: "アカウントロック中",
      body: "ログイン失敗によるロック",
      when: loginWhen,
    });
  // newest first
  return base.sort((x, y) => y.when.localeCompare(x.when)).slice(0, 10);
}
