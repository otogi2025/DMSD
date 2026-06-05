import React from "react";
import { RYO } from "../theme";
import { api } from "../api/client";
import type { TeacherOut, TeacherCreateIn } from "../api/types";

// 源 index.html 14147-14813（components/teachers-admin-page.jsx 块）。界面原样搬，仅作用域引用改写。
// /teachers-admin — 教员账号管理（2026-05-27 拍板）
// §3.4「前台不允许自助注册任何教师账号 / 必须先用现有教师账号登录 → 加 / 删」
// 接 backend: GET /teachers (list) / POST /teachers (创建) / DELETE /teachers/{id}
// 权限: backend 限「寮务部长 / 寮务课长 / 寮监 / 学习担当」(/teachers.py INVITE_ALLOWED_ROLES)
//       前端不提前判 — 让 backend 返 403 时显示错误（避免角色 string 双写漂移）

export function TeachersAdminPage({
  authToken,
  currentTeacherId,
}: {
  authToken: string;
  currentTeacherId: string;
}) {
  const T = RYO;
  const [list, setList] = React.useState<TeacherOut[] | null>(null); // null=加载中 / [] / [...]
  const [loadErr, setLoadErr] = React.useState<string | null>(null);
  const [showCreateModal, setShowCreateModal] = React.useState(false);
  const [confirmDelete, setConfirmDelete] = React.useState<TeacherOut | null>(
    null,
  );
  const [toast, setToast] = React.useState<{
    type: "ok" | "warn";
    msg: string;
  } | null>(null);

  const refresh = React.useCallback(() => {
    setList(null);
    setLoadErr(null);
    api
      .listTeachers(authToken)
      .then((rows) => setList(rows || []))
      .catch((e) => {
        console.warn("[TeachersAdmin] listTeachers 失败", e);
        setLoadErr(
          e && e.status === 403
            ? "閲覧権限がありません（寮務部長 / 寮務課長 / 寮監）"
            : `読み込み失敗 ${e && e.status ? `(${e.status})` : ""}`,
        );
        setList([]);
      });
  }, [authToken]);

  React.useEffect(() => {
    if (authToken) refresh();
  }, [authToken, refresh]);

  React.useEffect(() => {
    if (toast) {
      const id = setTimeout(() => setToast(null), 4000);
      return () => clearTimeout(id);
    }
  }, [toast]);

  const handleCreate = async (
    body: TeacherCreateIn,
  ): Promise<{ ok: boolean; error?: string }> => {
    try {
      await api.createTeacher(body, authToken);
      setToast({
        type: "ok",
        msg: `${body.name} 先生を追加しました`,
      });
      setShowCreateModal(false);
      refresh();
      return { ok: true };
    } catch (e: any) {
      console.warn("[TeachersAdmin] createTeacher 失败", e);
      const msg =
        e && e.message
          ? e.message
          : `追加に失敗しました (${e && e.status ? e.status : "?"})`;
      return { ok: false, error: msg };
    }
  };

  const handleDelete = async (t: TeacherOut) => {
    try {
      await api.deleteTeacher(t.id, authToken);
      setToast({ type: "ok", msg: `${t.name} 先生を削除しました` });
      setConfirmDelete(null);
      refresh();
    } catch (e: any) {
      console.warn("[TeachersAdmin] deleteTeacher 失败", e);
      const msg =
        e && e.message
          ? e.message
          : `削除に失敗しました (${e && e.status ? e.status : "?"})`;
      setToast({ type: "warn", msg });
      setConfirmDelete(null);
    }
  };

  return (
    <div style={{ padding: "8px 4px 32px" }}>
      <div
        style={{
          display: "flex",
          alignItems: "flex-end",
          gap: 16,
          marginBottom: 18,
        }}
      >
        <div style={{ flex: 1 }}>
          <div style={{ fontSize: 20, fontWeight: 700 }}>
            教員アカウント管理
          </div>
          <div style={{ fontSize: 12, color: T.ink3, marginTop: 4 }}>
            新しい宿監が来た時に追加・退任時に削除します（§3.4）
          </div>
        </div>
        <button
          type="button"
          onClick={() => setShowCreateModal(true)}
          style={{
            padding: "10px 18px",
            background: T.cobalt,
            color: "#fff",
            border: "none",
            borderRadius: 10,
            fontFamily: "inherit",
            fontSize: 13,
            fontWeight: 600,
            cursor: "pointer",
          }}
        >
          + 新規教員を追加
        </button>
      </div>

      {list === null && (
        <div
          style={{
            padding: 40,
            textAlign: "center",
            color: T.ink3,
            fontSize: 13,
          }}
        >
          教員一覧を読み込み中…
        </div>
      )}
      {list !== null && loadErr && (
        <div
          style={{
            padding: "16px 18px",
            background: T.dangerSoft,
            color: T.danger,
            border: `1px solid ${T.dangerBorder}`,
            borderRadius: 10,
            fontSize: 13,
          }}
        >
          {loadErr}
        </div>
      )}
      {list !== null && !loadErr && (
        <div
          style={{
            background: T.surface,
            border: `1px solid ${T.line}`,
            borderRadius: 12,
            overflow: "hidden",
          }}
        >
          <div
            style={{
              display: "grid",
              gridTemplateColumns:
                "minmax(120px, 1fr) minmax(120px, 1fr) minmax(160px, 1.4fr) minmax(120px, 1fr) minmax(80px, 0.6fr) 100px",
              gap: 12,
              padding: "12px 18px",
              background: T.surfaceAlt,
              borderBottom: `1px solid ${T.line}`,
              fontSize: 11,
              color: T.ink3,
              fontWeight: 600,
            }}
          >
            <div>氏名</div>
            <div>ログイン ID</div>
            <div>メール</div>
            <div>役職</div>
            <div>担当寮</div>
            <div style={{ textAlign: "right" }}>操作</div>
          </div>
          {list.length === 0 && (
            <div
              style={{
                padding: 40,
                textAlign: "center",
                color: T.ink3,
                fontSize: 13,
              }}
            >
              登録された教員がいません
            </div>
          )}
          {list.map((t) => {
            const dormLabel =
              t.assigned_dorm == null
                ? "—"
                : t.assigned_dorm === 4
                  ? "女寮"
                  : "男寮";
            const isSelf = t.id === currentTeacherId;
            return (
              <div
                key={t.id}
                style={{
                  display: "grid",
                  gridTemplateColumns:
                    "minmax(120px, 1fr) minmax(120px, 1fr) minmax(160px, 1.4fr) minmax(120px, 1fr) minmax(80px, 0.6fr) 100px",
                  gap: 12,
                  padding: "12px 18px",
                  borderBottom: `1px solid ${T.line}`,
                  fontSize: 13,
                  alignItems: "center",
                }}
              >
                <div style={{ fontWeight: 600 }}>
                  {t.name}
                  {isSelf && (
                    <span
                      style={{
                        marginLeft: 6,
                        fontSize: 10,
                        color: T.cobalt,
                        padding: "2px 6px",
                        background: T.cobaltSoft,
                        borderRadius: 999,
                      }}
                    >
                      自分
                    </span>
                  )}
                </div>
                <div style={{ fontFamily: T.mono, color: T.ink2 }}>
                  {t.login_id}
                </div>
                <div
                  style={{
                    color: T.ink2,
                    overflow: "hidden",
                    textOverflow: "ellipsis",
                    whiteSpace: "nowrap",
                  }}
                >
                  {t.email}
                </div>
                <div style={{ color: T.ink2 }}>{t.role}</div>
                <div style={{ color: T.ink2 }}>{dormLabel}</div>
                <div style={{ textAlign: "right" }}>
                  <button
                    type="button"
                    disabled={isSelf}
                    onClick={() => !isSelf && setConfirmDelete(t)}
                    title={isSelf ? "自分自身は削除できません" : ""}
                    style={{
                      padding: "6px 12px",
                      background: isSelf ? T.surfaceAlt : T.dangerSoft,
                      color: isSelf ? T.ink3 : T.danger,
                      border: `1px solid ${isSelf ? T.line : T.dangerBorder}`,
                      borderRadius: 8,
                      fontFamily: "inherit",
                      fontSize: 12,
                      cursor: isSelf ? "not-allowed" : "pointer",
                    }}
                  >
                    削除
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {showCreateModal && (
        <TeachersAdminCreateModal
          onCancel={() => setShowCreateModal(false)}
          onSubmit={handleCreate}
        />
      )}
      {confirmDelete && (
        <TeachersAdminConfirmDelete
          teacher={confirmDelete}
          onCancel={() => setConfirmDelete(null)}
          onConfirm={() => handleDelete(confirmDelete)}
        />
      )}
      {toast && (
        <div
          style={{
            position: "fixed",
            bottom: 24,
            right: 24,
            padding: "12px 18px",
            // 迁移修正：旧 index.html 成功提示误用 T.success*（RYO 无此 key→透明无色，旧 bug），新版统一真实存在的 T.ok*（绿）
            background: toast.type === "ok" ? T.okSoft : T.dangerSoft,
            color: toast.type === "ok" ? T.ok : T.danger,
            border: `1px solid ${toast.type === "ok" ? T.okBorder : T.dangerBorder}`,
            borderRadius: 10,
            fontSize: 13,
            fontWeight: 600,
            boxShadow: T.shadow2,
            zIndex: 1000,
          }}
        >
          {toast.msg}
        </div>
      )}
    </div>
  );
}

// 私有子组件：新增教员弹窗
function TeachersAdminCreateModal({
  onCancel,
  onSubmit,
}: {
  onCancel: () => void;
  onSubmit: (body: TeacherCreateIn) => Promise<{ ok: boolean; error?: string }>;
}) {
  const T = RYO;
  const [name, setName] = React.useState("");
  const [loginId, setLoginId] = React.useState("");
  const [email, setEmail] = React.useState("");
  const [password, setPassword] = React.useState("");
  const [role, setRole] = React.useState("寮監");
  const [assignedDorm, setAssignedDorm] = React.useState("");
  const [submitting, setSubmitting] = React.useState(false);
  const [err, setErr] = React.useState("");

  const ROLES = [
    "寮務部長",
    "寮務課長",
    "国際交流部長",
    "国際交流課長",
    "管理係",
    "寮監",
    "学習担当",
    "寮務一般教師",
  ];

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (submitting) return;
    if (
      !name.trim() ||
      !loginId.trim() ||
      !email.trim() ||
      !password ||
      password.length < 8
    ) {
      setErr("全項目を入力してください（パスワードは 8 文字以上）");
      return;
    }
    setSubmitting(true);
    setErr("");
    const result = await onSubmit({
      login_id: loginId.trim(),
      name: name.trim(),
      email: email.trim(),
      password,
      role,
      assigned_dorm: assignedDorm === "" ? undefined : Number(assignedDorm),
    });
    setSubmitting(false);
    if (!result.ok) setErr(result.error || "");
  };

  return (
    <div
      style={{
        position: "fixed",
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        background: "rgba(0,0,0,.4)",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        zIndex: 1000,
        padding: 24,
      }}
      onClick={onCancel}
    >
      <form
        onSubmit={submit}
        onClick={(e) => e.stopPropagation()}
        style={{
          background: T.surface,
          borderRadius: 14,
          padding: "26px 28px",
          width: 460,
          maxHeight: "90vh",
          overflowY: "auto",
          boxShadow: T.shadow2,
        }}
      >
        <div style={{ fontSize: 18, fontWeight: 700, marginBottom: 4 }}>
          新規教員を追加
        </div>
        <div style={{ fontSize: 12, color: T.ink3, marginBottom: 18 }}>
          追加後、新しい先生はログイン画面で自分のカードを選びパスワードを入力できます
        </div>

        <AdminField label="氏名" value={name} onChange={setName} autoFocus />
        <AdminField
          label="ログイン ID（半角英数）"
          value={loginId}
          onChange={setLoginId}
        />
        <AdminField
          label="メールアドレス"
          value={email}
          onChange={setEmail}
          type="email"
        />
        <AdminField
          label="初期パスワード（8 文字以上）"
          value={password}
          onChange={setPassword}
          type="password"
        />

        <label style={{ display: "block", marginBottom: 14 }}>
          <div
            style={{
              fontSize: 11,
              color: T.ink2,
              marginBottom: 6,
              fontWeight: 600,
            }}
          >
            役職
          </div>
          <select
            value={role}
            onChange={(e) => setRole(e.target.value)}
            style={{
              width: "100%",
              padding: "10px 12px",
              border: `1px solid ${T.lineStrong}`,
              borderRadius: 8,
              fontFamily: "inherit",
              fontSize: 14,
              background: T.surface,
              color: T.ink,
            }}
          >
            {ROLES.map((r) => (
              <option key={r} value={r}>
                {r}
              </option>
            ))}
          </select>
        </label>

        <label style={{ display: "block", marginBottom: 14 }}>
          <div
            style={{
              fontSize: 11,
              color: T.ink2,
              marginBottom: 6,
              fontWeight: 600,
            }}
          >
            担当寮
          </div>
          <select
            value={assignedDorm}
            onChange={(e) => setAssignedDorm(e.target.value)}
            style={{
              width: "100%",
              padding: "10px 12px",
              border: `1px solid ${T.lineStrong}`,
              borderRadius: 8,
              fontFamily: "inherit",
              fontSize: 14,
              background: T.surface,
              color: T.ink,
            }}
          >
            <option value="">跨寮（指定なし）</option>
            <option value="1">男一寮</option>
            <option value="2">男二寮</option>
            <option value="4">女寮</option>
          </select>
        </label>

        {err && (
          <div
            style={{
              marginBottom: 12,
              padding: "8px 12px",
              fontSize: 12,
              background: T.dangerSoft,
              color: T.danger,
              border: `1px solid ${T.dangerBorder}`,
              borderRadius: 8,
            }}
          >
            {err}
          </div>
        )}

        <div
          style={{
            display: "flex",
            gap: 10,
            justifyContent: "flex-end",
            marginTop: 6,
          }}
        >
          <button
            type="button"
            onClick={onCancel}
            style={{
              padding: "10px 18px",
              background: "transparent",
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
            type="submit"
            disabled={submitting}
            style={{
              padding: "10px 18px",
              background: submitting ? T.lineStrong : T.cobalt,
              color: "#fff",
              border: "none",
              borderRadius: 8,
              fontFamily: "inherit",
              fontSize: 13,
              fontWeight: 600,
              cursor: submitting ? "not-allowed" : "pointer",
            }}
          >
            {submitting ? "追加中…" : "追加"}
          </button>
        </div>
      </form>
    </div>
  );
}

// 私有子组件：删除确认弹窗
function TeachersAdminConfirmDelete({
  teacher,
  onCancel,
  onConfirm,
}: {
  teacher: TeacherOut;
  onCancel: () => void;
  onConfirm: () => void;
}) {
  const T = RYO;
  return (
    <div
      style={{
        position: "fixed",
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        background: "rgba(0,0,0,.4)",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        zIndex: 1000,
        padding: 24,
      }}
      onClick={onCancel}
    >
      <div
        onClick={(e) => e.stopPropagation()}
        style={{
          background: T.surface,
          borderRadius: 14,
          padding: "24px 28px",
          width: 420,
          boxShadow: T.shadow2,
        }}
      >
        <div style={{ fontSize: 17, fontWeight: 700, marginBottom: 6 }}>
          {teacher.name} 先生のアカウントを削除しますか？
        </div>
        <div style={{ fontSize: 12, color: T.ink3, marginBottom: 20 }}>
          削除すると{teacher.name}
          先生はログインできなくなります。これまでの点呼・申請履歴は残ります。
        </div>
        <div
          style={{
            display: "flex",
            gap: 10,
            justifyContent: "flex-end",
          }}
        >
          <button
            type="button"
            onClick={onCancel}
            style={{
              padding: "10px 18px",
              background: "transparent",
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
            type="button"
            onClick={onConfirm}
            style={{
              padding: "10px 18px",
              background: T.danger,
              color: "#fff",
              border: "none",
              borderRadius: 8,
              fontFamily: "inherit",
              fontSize: 13,
              fontWeight: 600,
              cursor: "pointer",
            }}
          >
            削除する
          </button>
        </div>
      </div>
    </div>
  );
}

// 私有子组件：单行表单字段（标签 + 输入框）
function AdminField({
  label,
  value,
  onChange,
  type = "text",
  autoFocus,
}: {
  label: string;
  value: string;
  onChange: (v: string) => void;
  type?: string;
  autoFocus?: boolean;
}) {
  const T = RYO;
  return (
    <label style={{ display: "block", marginBottom: 14 }}>
      <div
        style={{
          fontSize: 11,
          color: T.ink2,
          marginBottom: 6,
          fontWeight: 600,
        }}
      >
        {label}
      </div>
      <input
        type={type}
        value={value}
        autoFocus={autoFocus}
        onChange={(e) => onChange(e.target.value)}
        style={{
          width: "100%",
          padding: "10px 12px",
          border: `1px solid ${T.lineStrong}`,
          borderRadius: 8,
          fontFamily: "inherit",
          fontSize: 14,
          background: T.surface,
          color: T.ink,
          outline: "none",
          boxSizing: "border-box",
        }}
      />
    </label>
  );
}
