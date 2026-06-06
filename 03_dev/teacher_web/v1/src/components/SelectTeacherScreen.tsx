import React from "react";
import { RYO } from "../theme";
import { APP_VERSION } from "../theme";
import { dormLabel } from "../theme";
import { ConfirmModal } from "./shared";
import tomoshibiIcon from "../assets/tomoshibi-icon.png";

// 源 index.html 10645-11295（components/select-teacher.jsx 块）。
// 页面：/login/select-teacher — 从「男性寮 / 女性寮」两栏里选今天值班的老师卡片。
// 编辑模式：可删除 + 追加老师；所在栏决定老师的担当寮。
// 仅作用域引用改写：window.RYO→RYO / window.APP_VERSION→APP_VERSION /
//   window.dormLabel→dormLabel / ConfirmModal 从 ./shared import；界面布局与样式一字未改。

// 老师卡片的 UI 视图模型（前端组装的形状，非后端 TeacherPublic）：
// id / dorm（"men" | "women"）/ name / initial（头像首字）/ lastLoginMins（距上次登录的分钟数）
interface TeacherVM {
  id: string;
  dorm: "men" | "women";
  name: string;
  initial: string;
  lastLoginMins: number | null;
}

// 品牌图标用 Vite 资产 import（构建产出带哈希 URL）。

export function SelectTeacherScreen({
  teachers,
  lastTeacherId,
  onPick,
  onDeleteTeacher,
  onAddTeacher,
  onLogout,
}: {
  teachers: TeacherVM[];
  lastTeacherId: string | null;
  onPick: (t: TeacherVM) => void;
  onDeleteTeacher: (id: string) => void;
  onAddTeacher: (data: {
    dorm: "men" | "women";
    name: string;
    initial: string;
  }) => void;
  onLogout: () => void;
}) {
  const T = RYO;
  const [edit, setEdit] = React.useState(false);
  const [confirmDelete, setConfirmDelete] = React.useState<TeacherVM | null>(
    null,
  );
  const [addModal, setAddModal] = React.useState<{
    dorm: "men" | "women";
  } | null>(null);

  const men = teachers.filter((t) => t.dorm === "men");
  const women = teachers.filter((t) => t.dorm === "women");

  return (
    <div
      style={{
        minHeight: "100vh",
        background: T.paper,
        color: T.ink,
        fontFamily: T.font,
        padding: "36px 48px",
        position: "relative",
      }}
    >
      {/* 页头 */}
      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: 16,
          marginBottom: 28,
        }}
      >
        <img
          src={tomoshibiIcon}
          alt="Tomoshibi"
          style={{ width: 44, height: 44, borderRadius: 11 }}
        />
        <div>
          <div style={{ fontSize: 22, fontWeight: 700, letterSpacing: -0.2 }}>
            担当者を選んでください
          </div>
          <div style={{ fontSize: 13, color: T.ink3, marginTop: 2 }}>
            本日の点呼を担当する先生のカードを押してください
          </div>
        </div>
        <div style={{ flex: 1 }} />
        <button
          onClick={onLogout}
          style={{
            padding: "8px 14px",
            background: "transparent",
            color: T.ink3,
            border: `1px solid ${T.lineStrong}`,
            borderRadius: 8,
            fontFamily: "inherit",
            fontSize: 12,
            cursor: "pointer",
          }}
        >
          ログアウト
        </button>
      </div>

      {/* 两栏 */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "1fr 1fr",
          gap: 32,
          maxWidth: 1100,
        }}
      >
        <DormColumn
          label="男子寮"
          icon="M"
          accent={T.maleAccent}
          soft={T.maleSoft}
          dorm="men"
          teachers={men}
          lastTeacherId={lastTeacherId}
          edit={edit}
          onPick={onPick}
          onDelete={(t) => setConfirmDelete(t)}
          onAdd={() => setAddModal({ dorm: "men" })}
        />
        <DormColumn
          label="女子寮"
          icon="F"
          accent={T.femaleAccent}
          soft={T.femaleSoft}
          dorm="women"
          teachers={women}
          lastTeacherId={lastTeacherId}
          edit={edit}
          onPick={onPick}
          onDelete={(t) => setConfirmDelete(t)}
          onAdd={() => setAddModal({ dorm: "women" })}
        />
      </div>

      {/* 悬浮的编辑按钮（FAB） */}
      <button
        onClick={() => setEdit(!edit)}
        style={{
          position: "fixed",
          right: 36,
          bottom: 36,
          width: edit ? "auto" : 64,
          height: 64,
          padding: edit ? "0 24px" : 0,
          borderRadius: 32,
          background: edit ? T.cobalt : T.ink,
          color: "#fff",
          border: "none",
          cursor: "pointer",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          gap: 8,
          fontFamily: "inherit",
          fontSize: 14,
          fontWeight: 700,
          boxShadow: "0 8px 24px rgba(20,23,31,.28)",
          transition: "all .18s",
        }}
      >
        {edit ? (
          <>
            <span>✓</span>
            <span>完了</span>
          </>
        ) : (
          <PencilIcon />
        )}
      </button>

      {/* 页脚 */}
      <div
        style={{
          position: "absolute",
          bottom: 18,
          left: 48,
          fontSize: 11,
          color: T.ink3,
        }}
      >
        Tomoshibi {APP_VERSION}・担当者は30分操作がないと自動で本画面に戻ります
      </div>

      {confirmDelete && (
        <ConfirmModal
          title={`${confirmDelete.name} 先生のアカウントを削除しますか？`}
          desc="削除すると本画面から候補が消えます。点呼履歴は残ります。"
          danger
          confirmLabel="削除"
          onCancel={() => setConfirmDelete(null)}
          onConfirm={() => {
            onDeleteTeacher(confirmDelete.id);
            setConfirmDelete(null);
          }}
        />
      )}
      {addModal && (
        <AddTeacherModal
          dorm={addModal.dorm}
          onCancel={() => setAddModal(null)}
          onAdd={(data) => {
            onAddTeacher({ dorm: addModal.dorm, ...data });
            setAddModal(null);
          }}
        />
      )}
    </div>
  );
}

// 单个寮的栏目（男性寮 / 女性寮）：标题 + 老师卡片列表 + 编辑模式下的追加卡片
function DormColumn({
  label,
  icon,
  accent,
  soft,
  dorm,
  teachers,
  lastTeacherId,
  edit,
  onPick,
  onDelete,
  onAdd,
}: {
  label: string;
  icon: string;
  accent: string;
  soft: string;
  dorm: "men" | "women";
  teachers: TeacherVM[];
  lastTeacherId: string | null;
  edit: boolean;
  onPick: (t: TeacherVM) => void;
  onDelete: (t: TeacherVM) => void;
  onAdd: () => void;
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
          <TeacherCard
            key={t.id}
            t={t}
            isLast={t.id === lastTeacherId}
            edit={edit}
            onPick={onPick}
            onDelete={onDelete}
          />
        ))}
        {edit && <AddCard onClick={onAdd} />}
      </div>
    </div>
  );
}

// 单张老师卡片：头像 + 姓名 + 上次登录文案；编辑模式下右上角带删除按钮，最近一次担当者带「前回」标记
function TeacherCard({
  t,
  isLast,
  edit,
  onPick,
  onDelete,
}: {
  t: TeacherVM;
  isLast: boolean;
  edit: boolean;
  onPick: (t: TeacherVM) => void;
  onDelete: (t: TeacherVM) => void;
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
    <div style={{ position: "relative" }}>
      <button
        onClick={() => !edit && onPick(t)}
        disabled={edit}
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
          cursor: edit ? "default" : "pointer",
          fontFamily: "inherit",
          textAlign: "left",
          transition: "all .12s",
          minHeight: 88,
        }}
        onMouseEnter={(e) =>
          !edit &&
          ((e.currentTarget.style.boxShadow = T.shadow2),
          (e.currentTarget.style.transform = "translateY(-1px)"))
        }
        onMouseLeave={(e) => (
          (e.currentTarget.style.boxShadow = T.shadow1),
          (e.currentTarget.style.transform = "translateY(0)")
        )}
      >
        <div
          style={{
            width: 48,
            height: 48,
            borderRadius: 24,
            background: T.cobaltSoft,
            color: T.cobaltDeep,
            fontSize: 18,
            fontWeight: 700,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            flexShrink: 0,
          }}
        >
          {t.initial}
        </div>
        <div style={{ flex: 1, minWidth: 0 }}>
          <div style={{ fontSize: 17, fontWeight: 700, color: T.ink }}>
            {t.name}{" "}
            <span style={{ fontSize: 13, fontWeight: 500, color: T.ink3 }}>
              先生
            </span>
          </div>
          <div style={{ fontSize: 12, color: T.ink3, marginTop: 3 }}>
            {loginText}
          </div>
        </div>
        {isLast && !edit && (
          <span
            style={{
              fontSize: 10,
              fontWeight: 700,
              color: T.cobaltDeep,
              background: T.cobaltSoft,
              padding: "3px 8px",
              borderRadius: 4,
              letterSpacing: 1,
            }}
          >
            前回
          </span>
        )}
      </button>
      {edit && (
        <button
          onClick={() => onDelete(t)}
          style={{
            position: "absolute",
            top: -8,
            right: -8,
            width: 28,
            height: 28,
            borderRadius: 14,
            background: T.danger,
            color: "#fff",
            border: "2px solid #fff",
            cursor: "pointer",
            fontSize: 14,
            fontWeight: 700,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            animation: "popIn .18s ease-out",
            boxShadow: "0 4px 10px rgba(179,58,58,.4)",
          }}
        >
          ×
        </button>
      )}
    </div>
  );
}

// 编辑模式下的「教员を追加」虚线卡片
function AddCard({ onClick }: { onClick: () => void }) {
  const T = RYO;
  return (
    <button
      onClick={onClick}
      style={{
        padding: "18px 18px",
        background: "transparent",
        border: `2px dashed ${T.grayBorder}`,
        borderRadius: 14,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        gap: 10,
        cursor: "pointer",
        fontFamily: "inherit",
        color: T.ink3,
        minHeight: 88,
        fontSize: 13,
        fontWeight: 600,
        animation: "popIn .22s ease-out",
      }}
    >
      <span style={{ fontSize: 22, lineHeight: 1 }}>+</span>
      <span>教員を追加</span>
    </button>
  );
}

// 编辑按钮（FAB）非编辑态显示的铅笔图标
function PencilIcon() {
  return (
    <svg
      width="22"
      height="22"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="M12 20h9" />
      <path d="M16.5 3.5a2.1 2.1 0 013 3L7 19l-4 1 1-4L16.5 3.5z" />
    </svg>
  );
}

// 追加老师弹窗：填写氏名 + ふりがな，担当寮由所在栏自动判定
function AddTeacherModal({
  dorm,
  onCancel,
  onAdd,
}: {
  dorm: "men" | "women";
  onCancel: () => void;
  onAdd: (data: { name: string; initial: string }) => void;
}) {
  const T = RYO;
  const [name, setName] = React.useState("");
  const [furigana, setFurigana] = React.useState("");
  const ok = name.trim().length > 0;
  return (
    <div
      onClick={onCancel}
      style={{
        position: "fixed",
        inset: 0,
        background: "rgba(20,23,31,.48)",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        zIndex: 200,
      }}
    >
      <div
        onClick={(e) => e.stopPropagation()}
        style={{
          width: 460,
          background: T.surface,
          borderRadius: 14,
          boxShadow: T.shadowModal,
          padding: "24px 28px",
        }}
      >
        <div
          style={{
            fontSize: 11,
            color: T.ink3,
            letterSpacing: 2,
            fontWeight: 600,
          }}
        >
          教員を追加・{dormLabel(dorm)}
        </div>
        <div
          style={{
            fontSize: 18,
            fontWeight: 700,
            marginTop: 4,
            marginBottom: 18,
          }}
        >
          新しい先生を登録
        </div>
        <LField
          label="氏名（必須）"
          value={name}
          onChange={setName}
          autoFocus
        />
        <div style={{ marginBottom: 4 }}>
          <div
            style={{
              fontSize: 11,
              color: T.ink2,
              marginBottom: 6,
              fontWeight: 600,
            }}
          >
            ふりがな（検索用・任意）
          </div>
          <input
            value={furigana}
            onChange={(e) => setFurigana(e.target.value)}
            placeholder="たなか たろう"
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
        </div>
        <div style={{ fontSize: 11, color: T.ink3, marginTop: 12 }}>
          担当寮：<b style={{ color: T.ink2 }}>{dormLabel(dorm)}</b>
          （カラム位置で自動判定）
        </div>
        <div
          style={{
            display: "flex",
            justifyContent: "flex-end",
            gap: 8,
            marginTop: 22,
          }}
        >
          <button
            onClick={onCancel}
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
            キャンセル
          </button>
          <button
            disabled={!ok}
            onClick={() =>
              onAdd({ name: name.trim(), initial: name.trim().charAt(0) })
            }
            style={{
              padding: "9px 18px",
              background: ok ? T.cobalt : T.lineStrong,
              color: "#fff",
              border: "none",
              borderRadius: 8,
              fontFamily: "inherit",
              fontSize: 13,
              fontWeight: 700,
              cursor: ok ? "pointer" : "not-allowed",
            }}
          >
            追加
          </button>
        </div>
      </div>
    </div>
  );
}

// 带标签的输入框（氏名输入用）。
// ⚠️ 原 index.html 单文件源里 AddTeacherModal 引用了 <LField>，但全仓库（含所有 babel 块）
//    都没有 LField 的定义 —— 这是原始单文件里就存在的悬空引用（打开追加弹窗会运行时报错）。
//    迁移时按原样把该缺失组件补成本文件私有子组件：界面取与同源签名一致的 AdminField
//    （label / value / onChange / autoFocus，源 index.html 14770-14810）的样式，以恢复
//    原本「氏名 (必須)」输入框应有的渲染。详见返回的 notes。
function LField({
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
