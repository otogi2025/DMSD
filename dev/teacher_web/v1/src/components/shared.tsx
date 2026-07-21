import React from "react";
import { RYO, dormLabel, type RyoTokens } from "../theme";

// 跨多个页面复用的小组件 —— 从旧 index.html 各块原样搬（界面冻结）。
// ConfirmModal / DormBadge / StateBadge / StudentPicker 自带 RYO（内部 const T=RYO，不接收 T 参数）；
// ModalShell / ModalField / ModalFooter 沿用原 props 的 T 参数（调用方传 RYO）。
//
// web#139：ConfirmModal 与 ModalShell 共用同一套「全屏遮罩 + 点背景关闭 + 内容区 stopPropagation」
// 行为（仅 zIndex / 宽度 / 内头不同）。改无障碍 / Esc / 滚动锁定时两处必须同步改。

// 源 index.html 11065-11154（select-teacher 块）
export function ConfirmModal({
  title,
  desc,
  danger,
  confirmLabel,
  onCancel,
  onConfirm,
}: {
  title: string;
  desc?: string;
  danger?: boolean;
  confirmLabel?: string;
  onCancel: () => void;
  onConfirm: () => void;
}) {
  const T = RYO;
  return (
    // web#139：遮罩行为须与下方 ModalShell 同步（点背景关闭 / 内容 stopPropagation）
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
          width: 440,
          background: T.surface,
          borderRadius: 14,
          boxShadow: T.shadowModal,
          padding: "24px 28px",
        }}
      >
        <div style={{ fontSize: 17, fontWeight: 700 }}>{title}</div>
        {desc && (
          <div
            style={{
              fontSize: 13,
              color: T.ink3,
              marginTop: 8,
              lineHeight: 1.6,
            }}
          >
            {desc}
          </div>
        )}
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
            onClick={onConfirm}
            style={{
              padding: "9px 18px",
              background: danger ? T.danger : T.cobalt,
              color: "#fff",
              border: "none",
              borderRadius: 8,
              fontFamily: "inherit",
              fontSize: 13,
              fontWeight: 700,
              cursor: "pointer",
            }}
          >
            {confirmLabel || "確認"}
          </button>
        </div>
      </div>
    </div>
  );
}

// 源 index.html 11902-11921（shell 块）
export function DormBadge({ dorm }: { dorm: string }) {
  const T = RYO;
  const isMen = dorm === "men";
  return (
    <span
      style={{
        fontSize: 10,
        fontWeight: 700,
        padding: "2px 7px",
        borderRadius: 4,
        letterSpacing: 0.5,
        background: isMen ? T.maleSoft : T.femaleSoft,
        color: isMen ? T.maleAccent : T.femaleAccent,
        border: `1px solid ${isMen ? T.maleAccent : T.femaleAccent}33`,
      }}
    >
      {dormLabel(dorm)}
    </span>
  );
}

// 源 index.html 18534-18596（front-desk 块）
export function ModalShell({
  T,
  title,
  onClose,
  children,
}: {
  T: RyoTokens;
  title: string;
  onClose: () => void;
  children: React.ReactNode;
}) {
  return (
    // web#139：遮罩行为须与上方 ConfirmModal 同步（点背景关闭 / 内容 stopPropagation）
    <div
      onClick={onClose}
      style={{
        position: "fixed",
        inset: 0,
        background: "rgba(20,23,31,0.55)",
        zIndex: 90,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        padding: 20,
      }}
    >
      <div
        onClick={(e) => e.stopPropagation()}
        style={{
          background: T.surface,
          borderRadius: 14,
          width: 540,
          maxWidth: "100%",
          boxShadow: T.shadowModal,
          overflow: "hidden",
        }}
      >
        <div
          style={{
            padding: "16px 20px",
            borderBottom: `1px solid ${T.line}`,
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
          }}
        >
          <div style={{ fontSize: 15, fontWeight: 700 }}>{title}</div>
          <button
            onClick={onClose}
            style={{
              background: "transparent",
              border: "none",
              fontSize: 20,
              color: T.ink3,
              cursor: "pointer",
            }}
          >
            ×
          </button>
        </div>
        <div
          style={{
            padding: 20,
            display: "flex",
            flexDirection: "column",
            gap: 14,
          }}
        >
          {children}
        </div>
      </div>
    </div>
  );
}

// 源 index.html 18597-18613（front-desk 块的 Field，export 名 ModalField）
export function ModalField({
  T,
  label,
  children,
}: {
  T: RyoTokens;
  label: string;
  children: React.ReactNode;
}) {
  return (
    <div>
      <div
        style={{
          fontSize: 11,
          color: T.ink3,
          fontWeight: 600,
          letterSpacing: 1,
          marginBottom: 6,
        }}
      >
        {label}
      </div>
      {children}
    </div>
  );
}

// 源 index.html 18615-18660（front-desk 块）
export function ModalFooter({
  T,
  onClose,
  onSubmit,
  disabled,
  submitLabel, // web#41: 「却下」「設定」等场景可覆盖默认「登録」
}: {
  T: RyoTokens;
  onClose: () => void;
  onSubmit: () => void;
  disabled?: boolean;
  submitLabel?: string;
}) {
  return (
    <div
      style={{
        display: "flex",
        justifyContent: "flex-end",
        gap: 8,
        marginTop: 6,
      }}
    >
      <button
        onClick={onClose}
        style={{
          padding: "8px 16px",
          background: T.surface,
          color: T.ink2,
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
        onClick={onSubmit}
        disabled={disabled}
        style={{
          padding: "8px 16px",
          background: disabled ? T.line : T.cobalt,
          color: "#fff",
          border: "none",
          borderRadius: 8,
          fontFamily: "inherit",
          fontSize: 13,
          fontWeight: 700,
          cursor: disabled ? "not-allowed" : "pointer",
        }}
      >
        {/* web#41 */}
        {submitLabel || "登録"}
      </button>
    </div>
  );
}

// 源 index.html 16293-16317（applications 块；ApplicationsPage + OutstayDetailModal 跨块共用）
export function StateBadge({ s }: { s: string }) {
  const T = RYO;
  // 未知 state 退化成灰底显示原始字符串，不崩页（C8 兜底）。
  const map = (
    {
      pending: [T.warn, T.warnSoft, T.warnBorder, "審査待ち"],
      approved: [T.ok, T.okSoft, T.okBorder, "承認済"],
      rejected: [T.danger, T.dangerSoft, T.dangerBorder, "却下"],
      question: [T.cobalt, T.cobaltSoft, T.infoBorder, "質問あり"],
      withdrawn: [T.ink3, T.surfaceAlt, T.line, "撤回"],
      confirmed: [T.ok, T.okSoft, T.okBorder, "確認済"],
      revoked: [T.ink3, T.surfaceAlt, T.line, "取消"],
    } as Record<string, [string, string, string, string]>
  )[s] || [T.ink3, T.surfaceAlt, T.line, s];
  return (
    <span
      style={{
        fontSize: 11,
        fontWeight: 700,
        padding: "2px 8px",
        borderRadius: 4,
        background: map[1],
        color: map[0],
        border: `1px solid ${map[2]}`,
        letterSpacing: 0.5,
        whiteSpace: "nowrap",
      }}
    >
      {map[3]}
    </span>
  );
}

// ── 学生选择器（共用）── 2026-06-14 选学生统一改造
// 把原来散在「前台快递 / 事件记录 / 扣分页」各写各的「挑学生」收拢成一个组件。
//   mode="single" 单选：点一行即选定并收起，触发框显示「姓名（部屋号 · 学籍番号）」；
//   mode="multi"  多选：勾选累加成可删 chip（沿用原 StudentMultiSelect 的就地展开面板，
//                       不用 position:absolute 浮层、避免被表单 modal 的 overflow 裁掉）。
// searchApi 由调用方传入 → 适配三个权限不同的后端接口（前台 C_FRONTDESK / 账号管理
//   C_STUDENT_ACCOUNT / 扣分 C_DEMERIT），组件本身不绑死某个接口。
// 打开即拉学生（空查询也发）→ 不打字也能滚动点选；想筛再打字（250ms 防抖）。
// 展示上限由组件截断（最多 50 条），防空查询后端返管辖全量时 DOM 膨胀。
const PICKER_RESULT_LIMIT = 50;

export type PickerStudent = {
  id: string;
  name: string;
  room_no: string;
  student_no: string;
};

export function StudentPicker({
  mode,
  searchApi,
  selected,
  onChange,
  authToken,
  autoOpen,
  placeholder,
}: {
  mode: "single" | "multi";
  searchApi: (q: string, token: string) => Promise<PickerStudent[]>;
  selected: PickerStudent[];
  onChange: (next: PickerStudent[]) => void;
  authToken: string;
  autoOpen?: boolean; // 单选放在 modal 里时设 true → 打开即展开列表（itsuki「打开弹窗就直接列出」）
  placeholder?: string;
}) {
  const T = RYO;
  const [open, setOpen] = React.useState(!!autoOpen);
  const [query, setQuery] = React.useState("");
  const [results, setResults] = React.useState<PickerStudent[]>([]);
  const [loading, setLoading] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);
  const boxRef = React.useRef<HTMLDivElement>(null);
  // searchApi 多半是调用方内联箭头函数（每渲染换身份）→ 存 ref，effect 不依赖它、避免每次重渲染重拉。
  const searchApiRef = React.useRef(searchApi);
  searchApiRef.current = searchApi;

  // 点击选择器外部 → 收起
  React.useEffect(() => {
    if (!open) return;
    const h = (e: MouseEvent) => {
      if (boxRef.current && !boxRef.current.contains(e.target as Node)) {
        setOpen(false);
      }
    };
    document.addEventListener("mousedown", h);
    return () => document.removeEventListener("mousedown", h);
  }, [open]);

  // 展开 / 改搜索词 → 拉学生（250ms 防抖）。空查询也拉 → 打开即列表。
  React.useEffect(() => {
    // web#137：打开但无令牌 → 明示会话失效，别显示「該当なし」
    if (!open) return;
    if (!authToken) {
      setLoading(false);
      setResults([]);
      setError("セッションが切れました");
      return;
    }
    let cancelled = false;
    // web#132：loading 只在防抖到期、真正发请求前才置 true，打字期间保留上一批结果
    const timer = setTimeout(() => {
      setLoading(true);
      searchApiRef
        .current(query.trim(), authToken)
        .then((rows) => {
          if (cancelled) return;
          setResults(rows);
          setError(null);
          setLoading(false);
        })
        .catch((e) => {
          if (cancelled) return;
          setError(e.message || "学生リストの取得に失敗しました");
          setResults([]);
          setLoading(false);
        });
    }, 250);
    return () => {
      // web#133：cleanup 统一复位 loading，避免 cancelled 早返回把面板卡在「読み込み中…」
      cancelled = true;
      clearTimeout(timer);
      setLoading(false);
    };
  }, [open, query, authToken]);

  const isSelected = (id: string) => selected.some((s) => s.id === id);
  const pick = (s: PickerStudent) => {
    if (mode === "single") {
      onChange([s]);
      setOpen(false);
      setQuery("");
    } else if (isSelected(s.id)) {
      onChange(selected.filter((x) => x.id !== s.id));
    } else {
      onChange([...selected, s]);
    }
  };

  const sub = (s: PickerStudent) => `${s.room_no}号室 · ${s.student_no}`;
  // web#136：组件侧截断展示上限
  const displayResults = results.slice(0, PICKER_RESULT_LIMIT);

  return (
    <div ref={boxRef}>
      {/* 触发框 */}
      <div
        onClick={() => setOpen((o) => !o)}
        style={{
          width: "100%",
          minHeight: 40,
          padding: "6px 10px",
          border: `1px solid ${open ? T.cobalt : T.lineStrong}`,
          borderRadius: 8,
          background: T.surface,
          boxSizing: "border-box",
          cursor: "pointer",
          display: "flex",
          flexWrap: "wrap",
          gap: 6,
          alignItems: "center",
        }}
      >
        {mode === "single" ? (
          selected.length === 0 ? (
            <span style={{ fontSize: 13, color: T.ink3 }}>
              {placeholder || "学生を選択（クリックで一覧）"}
            </span>
          ) : (
            <span style={{ fontSize: 13, color: T.ink }}>
              <span style={{ fontWeight: 600 }}>{selected[0].name}</span>
              <span
                style={{
                  color: T.ink3,
                  fontSize: 12,
                  marginLeft: 8,
                  fontFamily: T.mono,
                }}
              >
                {sub(selected[0])}
              </span>
            </span>
          )
        ) : (
          <>
            {selected.length === 0 && (
              <span style={{ fontSize: 13, color: T.ink3 }}>
                {placeholder || "学生を選択（クリックで一覧）"}
              </span>
            )}
            {selected.map((s) => (
              <span
                key={s.id}
                onClick={(e) => e.stopPropagation()}
                style={{
                  display: "inline-flex",
                  alignItems: "center",
                  gap: 2,
                  padding: "2px 4px 2px 10px",
                  fontSize: 12,
                  color: T.cobalt,
                  background: T.cobaltSoft,
                  borderRadius: 999,
                }}
              >
                {s.name}
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    onChange(selected.filter((x) => x.id !== s.id));
                  }}
                  title="削除"
                  style={{
                    border: "none",
                    background: "transparent",
                    color: T.cobalt,
                    cursor: "pointer",
                    fontSize: 14,
                    lineHeight: 1,
                    padding: "0 4px",
                  }}
                >
                  ×
                </button>
              </span>
            ))}
          </>
        )}
        <span style={{ marginLeft: "auto", color: T.ink3, fontSize: 11 }}>
          {open ? "▲" : "▼"}
        </span>
      </div>

      {/* 就地展开面板：搜索框 + 列表 */}
      {open && (
        <div
          style={{
            marginTop: 6,
            border: `1px solid ${T.lineStrong}`,
            borderRadius: 10,
            overflow: "hidden",
            boxShadow: T.shadow1,
          }}
        >
          <div style={{ padding: 8, borderBottom: `1px solid ${T.line}` }}>
            <input
              autoFocus
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="名前・部屋番号・学籍番号で検索…"
              style={{
                width: "100%",
                padding: "7px 10px",
                border: `1px solid ${T.line}`,
                borderRadius: 6,
                fontFamily: "inherit",
                fontSize: 13,
                background: T.surfaceAlt,
                boxSizing: "border-box",
                outline: "none",
              }}
            />
          </div>
          <div style={{ maxHeight: 240, overflowY: "auto" }}>
            {loading && (
              <div
                style={{
                  padding: 16,
                  textAlign: "center",
                  color: T.ink3,
                  fontSize: 12,
                }}
              >
                読み込み中…
              </div>
            )}
            {!loading && error && (
              <div
                style={{
                  padding: 16,
                  textAlign: "center",
                  color: T.danger,
                  fontSize: 12,
                }}
              >
                ⚠️ {error}
              </div>
            )}
            {!loading && !error && displayResults.length === 0 && (
              <div
                style={{
                  padding: 16,
                  textAlign: "center",
                  color: T.ink3,
                  fontSize: 12,
                }}
              >
                該当する学生がいません
              </div>
            )}
            {!loading &&
              !error &&
              displayResults.map((s) => {
                const on = isSelected(s.id);
                return (
                  <div
                    key={s.id}
                    onClick={() => pick(s)}
                    style={{
                      display: "flex",
                      alignItems: "center",
                      gap: 10,
                      padding: "8px 12px",
                      cursor: "pointer",
                      fontSize: 13,
                      background: on ? T.cobaltSoft : "transparent",
                    }}
                  >
                    {mode === "multi" && (
                      <span
                        style={{
                          width: 16,
                          height: 16,
                          borderRadius: 4,
                          border: `1px solid ${on ? T.cobalt : T.lineStrong}`,
                          background: on ? T.cobalt : "transparent",
                          color: "#fff",
                          display: "flex",
                          alignItems: "center",
                          justifyContent: "center",
                          fontSize: 11,
                          flexShrink: 0,
                        }}
                      >
                        {on ? "✓" : ""}
                      </span>
                    )}
                    <span style={{ flex: 1, color: T.ink }}>{s.name}</span>
                    <span
                      style={{
                        fontSize: 11,
                        color: T.ink3,
                        fontFamily: T.mono,
                      }}
                    >
                      {sub(s)}
                    </span>
                  </div>
                );
              })}
          </div>
        </div>
      )}
    </div>
  );
}
