import React from "react";
import { RYO, APP_VERSION } from "../theme";
import { api } from "../api/client";
import type { TeacherProfile } from "../api/types";
import {
  GROUP_DORM_ADMIN,
  GROUP_GENERAL,
  GROUP_GENERAL_STUDY,
  GROUP_APPROVAL,
} from "../api/permissions";
import tomoshibiIcon from "../assets/tomoshibi-icon.png";

// 源 index.html 10068-10643（components/login.jsx 块）。界面原样搬。
// 品牌图标用 Vite 资产 import（构建产出带哈希 URL），渲染 <img src> 等价旧版。

// /login —— 实名账户 2 屏合一登录（2026-05-27 拍板，取代旧共用密码版）
//   屏 1 = 老师卡片列表（男寮 / 女寮 2 列，GET /teachers/public 无认证拿）
//   屏 2 = 选中老师后输该老师密码（teacher_id + password 调 POST /sessions/teacher）
// 旧 SelectTeacherScreen 中间页砍 —— 登录成功直接进 app。
// onLogin(token, profile, pickedTeacher) —— App 顶层一次性设 authToken+authProfile+teacher。

// 屏 1 加载老师列表后派生出的本地卡片形状（id/name/dorm/initial/lastLoginMins）
interface PickedTeacher {
  id: string;
  name: string;
  dorm: "men" | "women";
  permissionGroup: string | null;
  initial: string;
  lastLoginMins: number | null;
}

export function LoginScreen({
  onLogin,
  lastTeacherId,
}: {
  onLogin: (
    token: string,
    profile: TeacherProfile,
    pickedTeacher: PickedTeacher,
  ) => void;
  lastTeacherId: string | null;
}) {
  const T = RYO;
  const [teachers, setTeachers] = React.useState<PickedTeacher[] | null>(null); // null=loading / []=失败 / [...]=真值
  const [loadErr, setLoadErr] = React.useState<string | null>(null);
  const [picked, setPicked] = React.useState<PickedTeacher | null>(null);
  // 手动登录（「ログイン」入口）—— op / 临时账户不上墙，走输 login_id + 密码这条单独路
  const [manual, setManual] = React.useState(false);
  const [manualId, setManualId] = React.useState("");
  const [password, setPassword] = React.useState("");
  // 7-17 适老化拍板②：密码明文显示切换 — 年长用户打字慢易输错，盲打 + 3 次锁 30 分钟太凶
  const [showPw, setShowPw] = React.useState(false);
  // 登录时选今晚负责的寮（1=男子寮 / 4=女子寮）。除「申請承認専用」组外都要选，驱动后端寮过滤
  const [selectedDorm, setSelectedDorm] = React.useState<1 | 4 | null>(null);
  const [err, setErr] = React.useState("");
  const [submitting, setSubmitting] = React.useState(false);
  // web#33：去掉本地 fails 假锁计数 — 真锁只认服务器 423；剩余次数拿不到就不显

  // 该老师卡片是否需要选寮：申請承認専用组看全部、不用选；其他组要选
  const cardNeedsDorm = picked
    ? picked.permissionGroup !== GROUP_APPROVAL
    : false;

  // 屏 1 加载老师列表
  React.useEffect(() => {
    let cancelled = false;
    api
      .listTeachersPublic()
      .then((rows) => {
        if (cancelled) return;
        // backend assigned_dorm: 1/2 = 男寮 / 4 = 女寮 / null = 跨寮（暫归男寮列）
        const adapted: PickedTeacher[] = (rows || []).map((t) => ({
          id: t.id,
          name: t.name,
          dorm: t.assigned_dorm === 4 ? "women" : "men",
          permissionGroup: t.permission_group ?? null,
          initial: (t.name || "?").charAt(0),
          lastLoginMins: t.last_login_at
            ? Math.floor(
                (Date.now() - new Date(t.last_login_at).getTime()) / 60000,
              )
            : null,
        }));
        setTeachers(adapted);
      })
      .catch((e) => {
        if (cancelled) return;
        console.warn("[LoginScreen] listTeachersPublic 失败", e);
        setLoadErr(e && e.status ? `（${e.status}）` : "（接続失敗）");
        setTeachers([]);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  // web#33 / web#34：统一登录失败文案 — 423 为唯一已锁依据；401 不显假剩余次数；403 按 code 说明
  function loginFailMessage(
    err2: { status?: number; message?: string; code?: string } | null,
    wrongPwFallback: string,
  ): string {
    if (!err2) {
      return "サーバーに接続できません。しばらくしてから再度お試しください。";
    }
    if (err2.status === 401) {
      // web#33：只显后端 message / 密码错误，不数本地次数、不报假锁
      return err2.message || wrongPwFallback;
    }
    if (err2.status === 423) {
      return (
        err2.message ||
        "アカウントロック中。30 分ほど待ってから再度お試しください。"
      );
    }
    if (err2.status === 403) {
      // web#34：inactive / 临时账号过期给日语说明
      if (err2.code === "ACCOUNT_INACTIVE") {
        return (
          err2.message ||
          "このアカウントは停止中です。管理者にお問い合わせください。"
        );
      }
      if (err2.code === "ACCOUNT_EXPIRED") {
        return err2.message || "臨時アカウントの有効期限が切れています。";
      }
      return err2.message || "アクセスが拒否されました。";
    }
    if (err2.status) {
      // web#34：优先显示后端 message
      return err2.message || `サーバーエラー (${err2.status})`;
    }
    return "サーバーに接続できません。しばらくしてから再度お試しください。";
  }

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (submitting || !picked || !password) return;
    if (cardNeedsDorm && !selectedDorm) return; // 需选寮的组没选不放行
    setSubmitting(true);
    try {
      const data = await api.teacherLogin({
        teacher_id: picked.id,
        password,
        ...(selectedDorm ? { selected_dorm: selectedDorm } : {}),
      });
      setErr("");
      onLogin(data.access_token, data.teacher, picked);
    } catch (err2: any) {
      // web#33 / web#34
      setErr(loginFailMessage(err2, "パスワードが違います"));
      if (err2 && err2.status === 401) setPassword("");
    } finally {
      setSubmitting(false);
    }
  };

  // 手动登录提交（op 等不上墙的账号）—— 用 login_id + 密码，后端 POST /sessions/teacher 已支持 login_id
  const submitManual = async (e: React.FormEvent) => {
    e.preventDefault();
    if (submitting || !manualId || !password || !selectedDorm) return;
    setSubmitting(true);
    try {
      const data = await api.teacherLogin({
        login_id: manualId.trim(),
        password,
        selected_dorm: selectedDorm,
      });
      setErr("");
      // 手动登录没有卡片可选，用返回的老师档案现搭一个 PickedTeacher 给 App 顶层
      const t = data.teacher;
      const pk: PickedTeacher = {
        id: t.id,
        name: t.name,
        dorm: t.assigned_dorm === 4 ? "women" : "men",
        permissionGroup: t.permission_group ?? null,
        initial: (t.name || "?").charAt(0),
        lastLoginMins: null,
      };
      onLogin(data.access_token, data.teacher, pk);
    } catch (err2: any) {
      // web#33 / web#34（手动登录同口径）
      setErr(loginFailMessage(err2, "ID またはパスワードが違います"));
      if (err2 && err2.status === 401) setPassword("");
    } finally {
      setSubmitting(false);
    }
  };

  // 共通 brand header
  const brandHeader = (
    <div
      style={{
        display: "flex",
        alignItems: "center",
        gap: 14,
        marginBottom: 28,
        justifyContent: "center",
      }}
    >
      <img
        src={tomoshibiIcon}
        alt="Tomoshibi"
        style={{
          width: 48,
          height: 48,
          borderRadius: 12,
          boxShadow: T.shadow1,
        }}
      />
      <div>
        <div
          style={{
            fontSize: 22,
            fontWeight: 700,
            letterSpacing: 1,
            color: T.ink,
          }}
        >
          Tomoshibi
        </div>
        <div
          style={{
            fontSize: 11,
            color: T.ink3,
            letterSpacing: 1.5,
            marginTop: 2,
          }}
        >
          朝日塾 · 寮管理システム
        </div>
      </div>
    </div>
  );

  // —————— 屏 2：密码 ——————
  if (picked) {
    return (
      <div
        style={{
          minHeight: "100vh",
          background: T.paper,
          color: T.ink,
          fontFamily: T.font,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          padding: 24,
        }}
      >
        <div style={{ width: 420 }}>
          {brandHeader}
          <form
            onSubmit={submit}
            style={{
              background: T.surface,
              border: `1px solid ${T.line}`,
              borderRadius: 14,
              padding: "26px 28px 22px",
              boxShadow: T.shadow2,
            }}
          >
            <button
              type="button"
              onClick={() => {
                setPicked(null);
                setPassword("");
                setShowPw(false);
                setSelectedDorm(null);
                setErr("");
              }}
              style={{
                background: T.cobaltSoft,
                color: T.cobalt,
                border: "none",
                borderRadius: 6,
                padding: "8px 12px",
                fontFamily: "inherit",
                fontSize: 13,
                cursor: "pointer",
                marginBottom: 14,
              }}
            >
              ← 別の先生を選ぶ
            </button>
            <div
              style={{
                display: "flex",
                alignItems: "center",
                gap: 12,
                marginBottom: 18,
              }}
            >
              <div
                style={{
                  width: 44,
                  height: 44,
                  borderRadius: 22,
                  background: T.cobaltSoft,
                  color: T.cobalt,
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  fontSize: 18,
                  fontWeight: 700,
                }}
              >
                {picked.initial}
              </div>
              <div>
                <div style={{ fontSize: 18, fontWeight: 700 }}>
                  {picked.name} 先生
                </div>
              </div>
            </div>

            {/* 选今晚负责的寮（除「申請承認専用」组外）— 选的寮直接成为可见范围 */}
            {cardNeedsDorm && (
              <DormPicker value={selectedDorm} onChange={setSelectedDorm} />
            )}

            <label style={{ display: "block", marginBottom: 14 }}>
              <div
                style={{
                  fontSize: 11,
                  color: T.ink2,
                  marginBottom: 6,
                  fontWeight: 600,
                }}
              >
                パスワード
              </div>
              <div style={{ position: "relative" }}>
                <input
                  type={showPw ? "text" : "password"}
                  value={password}
                  autoFocus
                  onChange={(e) => {
                    setPassword(e.target.value);
                    setErr("");
                  }}
                  style={{
                    width: "100%",
                    padding: "11px 64px 11px 12px",
                    background: T.surface,
                    border: `1px solid ${T.lineStrong}`,
                    borderRadius: 8,
                    fontFamily: "inherit",
                    fontSize: 14,
                    color: T.ink,
                    outline: "none",
                    boxSizing: "border-box",
                  }}
                />
                <button
                  type="button"
                  onClick={() => setShowPw((v) => !v)}
                  style={{
                    position: "absolute",
                    right: 8,
                    top: "50%",
                    transform: "translateY(-50%)",
                    background: "transparent",
                    border: "none",
                    color: T.cobalt,
                    fontFamily: "inherit",
                    fontSize: 12,
                    fontWeight: 600,
                    cursor: "pointer",
                    padding: "4px 6px",
                  }}
                >
                  {showPw ? "隠す" : "表示"}
                </button>
              </div>
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

            <button
              type="submit"
              disabled={
                submitting || !password || (cardNeedsDorm && !selectedDorm)
              }
              style={{
                width: "100%",
                padding: "12px 16px",
                background:
                  submitting || !password || (cardNeedsDorm && !selectedDorm)
                    ? T.lineStrong
                    : T.cobalt,
                color: "#fff",
                border: "none",
                borderRadius: 10,
                fontFamily: "inherit",
                fontSize: 14,
                fontWeight: 600,
                cursor:
                  submitting || !password || (cardNeedsDorm && !selectedDorm)
                    ? "not-allowed"
                    : "pointer",
              }}
            >
              {submitting ? "認証中…" : "ログイン"}
            </button>
            {/* 7-17 适老化拍板①：寮没选时按钮灰着却零解释，年长用户会以为系统坏了 — 补一行原因 */}
            {cardNeedsDorm && !selectedDorm && (
              <div
                style={{
                  marginTop: 8,
                  fontSize: 12,
                  color: T.ink2,
                  textAlign: "center",
                }}
              >
                担当の寮を選んでください
              </div>
            )}
          </form>
          <div
            style={{
              fontSize: 11,
              color: T.ink3,
              textAlign: "center",
              marginTop: 14,
            }}
          >
            Tomoshibi {APP_VERSION}
          </div>
        </div>
      </div>
    );
  }

  // —————— 手动登录屏：「管理者ログイン」（op / 临时账户等不上墙的账号，输 login_id + 密码） ——————
  if (manual) {
    return (
      <div
        style={{
          minHeight: "100vh",
          background: T.paper,
          color: T.ink,
          fontFamily: T.font,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          padding: 24,
        }}
      >
        <div style={{ width: 420 }}>
          {brandHeader}
          <form
            onSubmit={submitManual}
            style={{
              background: T.surface,
              border: `1px solid ${T.line}`,
              borderRadius: 14,
              padding: "26px 28px 22px",
              boxShadow: T.shadow2,
            }}
          >
            <button
              type="button"
              onClick={() => {
                setManual(false);
                setManualId("");
                setPassword("");
                setShowPw(false);
                setSelectedDorm(null);
                setErr("");
              }}
              style={{
                background: T.cobaltSoft,
                color: T.cobalt,
                border: "none",
                borderRadius: 6,
                padding: "8px 12px",
                fontFamily: "inherit",
                fontSize: 13,
                cursor: "pointer",
                marginBottom: 14,
              }}
            >
              ← 先生一覧に戻る
            </button>
            <div style={{ fontSize: 18, fontWeight: 700, marginBottom: 4 }}>
              ログイン
            </div>
            <div style={{ fontSize: 11, color: T.ink3, marginBottom: 18 }}>
              ID とパスワードを入力してください
            </div>

            <label style={{ display: "block", marginBottom: 14 }}>
              <div
                style={{
                  fontSize: 11,
                  color: T.ink2,
                  marginBottom: 6,
                  fontWeight: 600,
                }}
              >
                管理 ID
              </div>
              <input
                type="text"
                value={manualId}
                autoFocus
                autoComplete="username"
                onChange={(e) => {
                  setManualId(e.target.value);
                  setErr("");
                }}
                style={{
                  width: "100%",
                  padding: "11px 12px",
                  background: T.surface,
                  border: `1px solid ${T.lineStrong}`,
                  borderRadius: 8,
                  fontFamily: "inherit",
                  fontSize: 14,
                  color: T.ink,
                  outline: "none",
                  boxSizing: "border-box",
                }}
              />
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
                パスワード
              </div>
              <div style={{ position: "relative" }}>
                <input
                  type={showPw ? "text" : "password"}
                  value={password}
                  autoComplete="current-password"
                  onChange={(e) => {
                    setPassword(e.target.value);
                    setErr("");
                  }}
                  style={{
                    width: "100%",
                    padding: "11px 64px 11px 12px",
                    background: T.surface,
                    border: `1px solid ${T.lineStrong}`,
                    borderRadius: 8,
                    fontFamily: "inherit",
                    fontSize: 14,
                    color: T.ink,
                    outline: "none",
                    boxSizing: "border-box",
                  }}
                />
                <button
                  type="button"
                  onClick={() => setShowPw((v) => !v)}
                  style={{
                    position: "absolute",
                    right: 8,
                    top: "50%",
                    transform: "translateY(-50%)",
                    background: "transparent",
                    border: "none",
                    color: T.cobalt,
                    fontFamily: "inherit",
                    fontSize: 12,
                    fontWeight: 600,
                    cursor: "pointer",
                    padding: "4px 6px",
                  }}
                >
                  {showPw ? "隠す" : "表示"}
                </button>
              </div>
            </label>

            {/* 手动登录前不知权限组，一律让选寮；op / 承認组账号后端会忽略此选择 */}
            <DormPicker value={selectedDorm} onChange={setSelectedDorm} />

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

            <button
              type="submit"
              disabled={submitting || !manualId || !password || !selectedDorm}
              style={{
                width: "100%",
                padding: "12px 16px",
                background:
                  submitting || !manualId || !password || !selectedDorm
                    ? T.lineStrong
                    : T.cobalt,
                color: "#fff",
                border: "none",
                borderRadius: 10,
                fontFamily: "inherit",
                fontSize: 14,
                fontWeight: 600,
                cursor:
                  submitting || !manualId || !password || !selectedDorm
                    ? "not-allowed"
                    : "pointer",
              }}
            >
              {submitting ? "認証中…" : "ログイン"}
            </button>
            {/* 7-17 适老化拍板①：手动登录屏同款 — 寮没选时说明按钮为什么灰着 */}
            {!selectedDorm && (
              <div
                style={{
                  marginTop: 8,
                  fontSize: 12,
                  color: T.ink2,
                  textAlign: "center",
                }}
              >
                担当の寮を選んでください
              </div>
            )}
          </form>
          <div
            style={{
              fontSize: 11,
              color: T.ink3,
              textAlign: "center",
              marginTop: 14,
            }}
          >
            Tomoshibi {APP_VERSION}
          </div>
        </div>
      </div>
    );
  }

  // —————— 屏 1：老师列表（按权限组分 4 栏；op 运维账号不上墙、走单独入口） ——————
  const tAll = teachers || [];
  const dormAdmin = tAll.filter((t) => t.permissionGroup === GROUP_DORM_ADMIN);
  const general = tAll.filter((t) => t.permissionGroup === GROUP_GENERAL);
  const generalStudy = tAll.filter(
    (t) => t.permissionGroup === GROUP_GENERAL_STUDY,
  );
  const approval = tAll.filter((t) => t.permissionGroup === GROUP_APPROVAL);

  return (
    <div
      style={{
        minHeight: "100vh",
        background: T.paper,
        color: T.ink,
        fontFamily: T.font,
        padding: "36px 48px",
      }}
    >
      {brandHeader}
      <div style={{ textAlign: "center", marginBottom: 22, color: T.ink2 }}>
        <div style={{ fontSize: 18, fontWeight: 700 }}>
          担当の先生を選んでください
        </div>
        <div style={{ fontSize: 12, color: T.ink3, marginTop: 4 }}>
          ご自分のお名前のカードを押すと、パスワード入力画面に進みます
        </div>
      </div>

      {teachers === null && (
        <div
          style={{
            textAlign: "center",
            padding: 60,
            color: T.ink3,
            fontSize: 13,
          }}
        >
          先生一覧を読み込み中…
        </div>
      )}

      {teachers !== null && teachers.length === 0 && (
        <div
          style={{
            maxWidth: 480,
            margin: "0 auto",
            padding: "20px 24px",
            background: T.dangerSoft,
            color: T.danger,
            border: `1px solid ${T.dangerBorder}`,
            borderRadius: 12,
            fontSize: 13,
            textAlign: "center",
          }}
        >
          先生一覧を取得できません {loadErr || ""}
          <div
            style={{
              fontSize: 11,
              color: T.ink3,
              marginTop: 8,
              fontFamily: T.mono,
            }}
          >
            サーバーに接続できません。管理者にお問い合わせください。
          </div>
        </div>
      )}

      {teachers !== null && teachers.length > 0 && (
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "1fr 1fr 1fr 1fr",
            gap: 20,
            maxWidth: 1280,
            margin: "0 auto",
          }}
        >
          <LoginGroupColumn
            label="寮管理者"
            icon="管"
            accent={T.cobalt}
            soft={T.cobaltSoft}
            teachers={dormAdmin}
            lastTeacherId={lastTeacherId}
            onPick={setPicked}
          />
          <LoginGroupColumn
            label="一般宿管"
            icon="般"
            accent={T.maleAccent}
            soft={T.maleSoft}
            teachers={general}
            lastTeacherId={lastTeacherId}
            onPick={setPicked}
          />
          <LoginGroupColumn
            label="一般宿管＋夜学習"
            icon="習"
            accent={T.femaleAccent}
            soft={T.femaleSoft}
            teachers={generalStudy}
            lastTeacherId={lastTeacherId}
            onPick={setPicked}
          />
          <LoginGroupColumn
            label="申請承認専用"
            icon="承"
            accent={T.cobalt}
            soft={T.cobaltSoft}
            teachers={approval}
            lastTeacherId={lastTeacherId}
            onPick={setPicked}
          />
        </div>
      )}

      <div style={{ textAlign: "center", marginTop: 36 }}>
        <button
          type="button"
          onClick={() => {
            setManual(true);
            setErr("");
          }}
          style={{
            background: "transparent",
            border: "none",
            color: T.ink3,
            fontFamily: "inherit",
            fontSize: 12,
            textDecoration: "underline",
            cursor: "pointer",
          }}
        >
          {/* 7-17 适老化拍板④：整页都是登录页、裸链接叫「ログイン」没人懂 — 点明是管理者入口 */}
          管理者ログイン
        </button>
        <div style={{ fontSize: 11, color: T.ink3, marginTop: 10 }}>
          Tomoshibi {APP_VERSION}
        </div>
      </div>
    </div>
  );
}

// 私有子组件 —— 今晚负责寮选择器（男子寮 / 女子寮）。
// 选的寮直接成为可见范围（申請承認専用 / op 组后端忽略此选择、看全部）。
function DormPicker({
  value,
  onChange,
}: {
  value: 1 | 4 | null;
  onChange: (d: 1 | 4) => void;
}) {
  const T = RYO;
  const opts: { v: 1 | 4; label: string; accent: string; soft: string }[] = [
    { v: 1, label: "男子寮", accent: T.maleAccent, soft: T.maleSoft },
    { v: 4, label: "女子寮", accent: T.femaleAccent, soft: T.femaleSoft },
  ];
  return (
    <div style={{ marginBottom: 14 }}>
      <div
        style={{
          fontSize: 11,
          color: T.ink2,
          marginBottom: 6,
          fontWeight: 600,
        }}
      >
        今夜の担当
      </div>
      <div style={{ display: "flex", gap: 8 }}>
        {opts.map((o) => {
          const on = value === o.v;
          return (
            <button
              key={o.v}
              type="button"
              onClick={() => onChange(o.v)}
              style={{
                flex: 1,
                padding: "10px 12px",
                background: on ? o.soft : T.surface,
                color: on ? o.accent : T.ink2,
                border: on
                  ? `2px solid ${o.accent}`
                  : `1px solid ${T.lineStrong}`,
                borderRadius: 8,
                fontFamily: "inherit",
                fontSize: 14,
                fontWeight: 700,
                cursor: "pointer",
              }}
            >
              {o.label}
            </button>
          );
        })}
      </div>
    </div>
  );
}

// 私有子组件 —— 一列（一个权限组），渲染该组的老师卡片
function LoginGroupColumn({
  label,
  icon,
  accent,
  soft,
  teachers,
  lastTeacherId,
  onPick,
}: {
  label: string;
  icon: string;
  accent: string;
  soft: string;
  teachers: PickedTeacher[];
  lastTeacherId: string | null;
  onPick: (t: PickedTeacher) => void;
}) {
  const T = RYO;
  return (
    <div>
      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: 10,
          marginBottom: 14,
        }}
      >
        <div
          style={{
            width: 32,
            height: 32,
            borderRadius: 8,
            background: soft,
            color: accent,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            fontSize: 15,
            fontWeight: 700,
            fontFamily: T.mono,
            border: `1px solid ${accent}33`,
          }}
        >
          {icon}
        </div>
        <div style={{ fontSize: 15, fontWeight: 700, letterSpacing: 1 }}>
          {label}
        </div>
        <div style={{ fontSize: 11, color: T.ink3, fontFamily: T.mono }}>
          {teachers.length} 名
        </div>
      </div>
      <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
        {teachers.map((t) => (
          <LoginTeacherCard
            key={t.id}
            t={t}
            isLast={t.id === lastTeacherId}
            onPick={onPick}
          />
        ))}
        {teachers.length === 0 && (
          <div
            style={{
              padding: "16px 18px",
              color: T.ink3,
              fontSize: 12,
              border: `1px dashed ${T.lineStrong}`,
              borderRadius: 12,
              textAlign: "center",
            }}
          >
            この権限グループの先生はいません
          </div>
        )}
      </div>
    </div>
  );
}

// 私有子组件 —— 单张老师卡片（头像 + 名字 + 最后登录时间 + 「前回」标记）
function LoginTeacherCard({
  t,
  isLast,
  onPick,
}: {
  t: PickedTeacher;
  isLast: boolean;
  onPick: (t: PickedTeacher) => void;
}) {
  const T = RYO;
  const loginText =
    t.lastLoginMins == null
      ? "初回ログイン"
      : t.lastLoginMins < 60
        ? `${t.lastLoginMins} 分前にログイン`
        : t.lastLoginMins < 60 * 24
          ? `${Math.floor(t.lastLoginMins / 60)} 時間前にログイン`
          : "本日未ログイン";
  return (
    <button
      type="button"
      onClick={() => onPick(t)}
      style={{
        width: "100%",
        padding: "14px 18px",
        background: T.surface,
        border: isLast ? `2px solid ${T.cobalt}` : `1px solid ${T.line}`,
        borderRadius: 14,
        boxShadow: T.shadow1,
        display: "flex",
        alignItems: "center",
        gap: 14,
        cursor: "pointer",
        fontFamily: "inherit",
        textAlign: "left",
        transition: "all .12s",
        minHeight: 88,
      }}
      onMouseEnter={(e) => {
        e.currentTarget.style.boxShadow = T.shadow2;
        e.currentTarget.style.transform = "translateY(-1px)";
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.boxShadow = T.shadow1;
        e.currentTarget.style.transform = "translateY(0)";
      }}
    >
      <div
        style={{
          width: 44,
          height: 44,
          borderRadius: 22,
          background: T.cobaltSoft,
          color: T.cobalt,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          fontSize: 18,
          fontWeight: 700,
          flexShrink: 0,
        }}
      >
        {(t.name || "?").charAt(0)}
      </div>
      <div style={{ flex: 1, minWidth: 0 }}>
        <div
          style={{
            fontSize: 16,
            fontWeight: 700,
            color: T.ink,
          }}
        >
          {t.name} 先生
        </div>
        <div
          style={{
            fontSize: 11,
            color: T.ink3,
            marginTop: 4,
            fontFamily: T.mono,
          }}
        >
          {loginText}
        </div>
      </div>
      {isLast && (
        <div
          style={{
            fontSize: 10,
            color: T.cobalt,
            fontWeight: 700,
            padding: "3px 8px",
            background: T.cobaltSoft,
            borderRadius: 999,
            flexShrink: 0,
          }}
        >
          前回
        </div>
      )}
    </button>
  );
}
