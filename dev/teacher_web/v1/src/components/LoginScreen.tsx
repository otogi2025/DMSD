import React from "react";
import { RYO, dormLabel, APP_VERSION } from "../theme";
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
  const [password, setPassword] = React.useState("");
  const [err, setErr] = React.useState("");
  const [submitting, setSubmitting] = React.useState(false);
  const [fails, setFails] = React.useState(0);

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

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (submitting || !picked || !password) return;
    setSubmitting(true);
    try {
      const data = await api.teacherLogin({
        teacher_id: picked.id,
        password,
      });
      setFails(0);
      setErr("");
      onLogin(data.access_token, data.teacher, picked);
    } catch (err2: any) {
      if (err2 && err2.status === 401) {
        const n = fails + 1;
        setFails(n);
        if (n >= 3) {
          setErr("3 回失敗しました。30 分間ロックされます。");
          setFails(0);
        } else {
          setErr(`パスワードが違います（残り ${3 - n} 回）`);
        }
        setPassword("");
      } else if (err2 && err2.status === 423) {
        setErr("アカウントロック中。30 分ほど待ってから再度お試しください。");
      } else if (err2 && err2.status) {
        setErr(`サーバーエラー (${err2.status})`);
      } else {
        setErr(
          "サーバーに接続できません。しばらくしてから再度お試しください。",
        );
      }
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
                setErr("");
                setFails(0);
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
                <div style={{ fontSize: 11, color: T.ink3, marginTop: 2 }}>
                  {dormLabel(picked.dorm)} 担当
                </div>
              </div>
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
                パスワード
              </div>
              <input
                type="password"
                value={password}
                autoFocus
                onChange={(e) => {
                  setPassword(e.target.value);
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
              disabled={submitting || !password}
              style={{
                width: "100%",
                padding: "12px 16px",
                background: submitting || !password ? T.lineStrong : T.cobalt,
                color: "#fff",
                border: "none",
                borderRadius: 10,
                fontFamily: "inherit",
                fontSize: 14,
                fontWeight: 600,
                cursor: submitting || !password ? "not-allowed" : "pointer",
              }}
            >
              {submitting ? "認証中…" : "ログイン"}
            </button>
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

      <div
        style={{
          fontSize: 11,
          color: T.ink3,
          textAlign: "center",
          marginTop: 36,
        }}
      >
        Tomoshibi {APP_VERSION}
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
            display: "flex",
            alignItems: "center",
            gap: 8,
          }}
        >
          {t.name} 先生
          <span
            style={{
              fontSize: 10,
              fontWeight: 600,
              color: t.dorm === "men" ? T.maleAccent : T.femaleAccent,
              background: t.dorm === "men" ? T.maleSoft : T.femaleSoft,
              padding: "2px 7px",
              borderRadius: 999,
            }}
          >
            {t.dorm === "men" ? "男子寮" : "女子寮"}
          </span>
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
