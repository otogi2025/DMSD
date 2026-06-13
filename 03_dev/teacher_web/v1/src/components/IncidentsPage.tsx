import React from "react";
import { RYO } from "../theme";
import { api } from "../api/client";
import { ConfirmModal } from "./shared";
import { StudentProfileModal } from "./StudentProfileModal";
import type { IncidentItem } from "../api/types";

// 源 index.html 27700-28342（accounts.jsx 块的 IncidentsPage）。界面原样搬，
// 仅作用域引用方式改写：window.RYO→RYO / window.tomoshibiApi→api /
// ConfirmModal、StudentProfileModal 改 import。

// toast 提示对象类型
type Toast = { type: "ok" | "err"; msg: string };

export function IncidentsPage({ authToken }: { authToken: string }) {
  const T = RYO;
  const [incidents, setIncidents] = React.useState<IncidentItem[]>([]);
  const [loading, setLoading] = React.useState(true);
  const [loadError, setLoadError] = React.useState<string | null>(null);
  const [showForm, setShowForm] = React.useState(false); // 新规录入表单显示
  const [editTarget, setEditTarget] = React.useState<IncidentItem | null>(null); // 编辑对象 incident
  const [toast, setToast] = React.useState<Toast | null>(null);
  const [confirmDelete, setConfirmDelete] = React.useState<IncidentItem | null>(
    null,
  ); // 软删除确认对象
  // 杭田 2026-06-04 五-6: 涉及学生姓名 chip 点击 → 开个人档案弹窗
  const [profileTarget, setProfileTarget] = React.useState<{
    id: string;
    name: string;
  } | null>(null);

  // 表单字段（新规 / 编辑 兼用）
  const [fTitle, setFTitle] = React.useState("");
  const [fBody, setFBody] = React.useState("");
  const [fDate, setFDate] = React.useState(
    new Date().toISOString().slice(0, 10),
  );
  // 关系学生：从「逗号分隔 UUID 手输」改为多选选择器，存 {id, name}
  const [fStudents, setFStudents] = React.useState<
    { id: string; name: string; sub?: string }[]
  >([]);
  const [fSubmitting, setFSubmitting] = React.useState(false);
  const [fError, setFError] = React.useState<string | null>(null);

  const fetchIncidents = React.useCallback(() => {
    if (!authToken) return;
    setLoading(true);
    setLoadError(null);
    api
      .listIncidents(authToken)
      .then((res) => {
        setIncidents(res.items || []);
        setLoading(false);
      })
      .catch((e) => {
        setLoadError(e.message || "事案リストの取得に失敗しました");
        setLoading(false);
      });
  }, [authToken]);

  React.useEffect(() => {
    fetchIncidents();
  }, [fetchIncidents]);

  React.useEffect(() => {
    if (toast) {
      const id = setTimeout(() => setToast(null), 3500);
      return () => clearTimeout(id);
    }
  }, [toast]);

  const openNew = () => {
    setEditTarget(null);
    setFTitle("");
    setFBody("");
    setFDate(new Date().toISOString().slice(0, 10));
    setFStudents([]);
    setFError(null);
    setShowForm(true);
  };

  const openEdit = (inc: IncidentItem) => {
    setEditTarget(inc);
    setFTitle(inc.title);
    setFBody(inc.body);
    setFDate(inc.incident_date);
    // 编辑回填：优先用后端带姓名的 involved_students；缺名时退回用 ID 当显示名
    setFStudents(
      (inc.involved_students || []).length > 0
        ? inc.involved_students.map((s) => ({ id: s.id, name: s.name }))
        : (inc.involved_student_ids || []).map((id) => ({ id, name: id })),
    );
    setFError(null);
    setShowForm(true);
  };

  const closeForm = () => {
    setShowForm(false);
    setEditTarget(null);
    setFError(null);
  };

  const submitForm = () => {
    if (!fTitle.trim()) {
      setFError("タイトルを入力してください");
      return;
    }
    if (!fBody.trim()) {
      setFError("内容を入力してください");
      return;
    }
    // 学生 ID 来自多选选择器（真实学生），无需再校验 UUID 格式
    const ids = fStudents.map((s) => s.id);
    setFSubmitting(true);
    setFError(null);

    const payload = {
      title: fTitle.trim(),
      body: fBody.trim(),
      involved_student_ids: ids,
      incident_date: fDate,
    };

    const call = editTarget
      ? api.updateIncident(editTarget.id, payload, authToken)
      : api.createIncident(payload, authToken);

    call
      .then((saved) => {
        if (editTarget) {
          setIncidents((list) =>
            list.map((inc) => (inc.id === saved.id ? saved : inc)),
          );
          setToast({ type: "ok", msg: "事案を更新しました" });
        } else {
          setIncidents((list) => [saved, ...list]);
          setToast({ type: "ok", msg: "事案を登録しました" });
        }
        closeForm();
        setFSubmitting(false);
      })
      .catch((e) => {
        setFError(e.message || "登録失敗");
        setFSubmitting(false);
      });
  };

  const softDelete = (inc: IncidentItem) => {
    api
      .deleteIncident(inc.id, authToken)
      .then(() => {
        setIncidents((list) => list.filter((i) => i.id !== inc.id));
        setToast({ type: "ok", msg: `「${inc.title}」を削除しました` });
        setConfirmDelete(null);
      })
      .catch((e) => {
        setToast({ type: "err", msg: e.message || "削除失敗" });
        setConfirmDelete(null);
      });
  };

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
        寮務管理
      </div>
      <div
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          margin: "4px 0 20px",
        }}
      >
        <h1 style={{ fontSize: 24, fontWeight: 700, letterSpacing: -0.3 }}>
          事案記録
        </h1>
        <button
          onClick={openNew}
          style={{
            padding: "9px 18px",
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
          ＋ 新規登録
        </button>
      </div>

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

      {/* 一览表格 */}
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
            gridTemplateColumns: "120px 1fr 120px 100px 80px",
            background: T.surfaceAlt,
            fontSize: 11,
            color: T.ink2,
            fontWeight: 600,
            letterSpacing: 1,
            borderBottom: `1px solid ${T.line}`,
          }}
        >
          {["日付", "タイトル / 概要", "登録日時", "関係学生数", "操作"].map(
            (h) => (
              <div key={h} style={{ padding: "10px 12px" }}>
                {h}
              </div>
            ),
          )}
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
        {!loading && incidents.length === 0 && (
          <div
            style={{
              padding: 40,
              textAlign: "center",
              color: T.ink3,
              fontSize: 13,
            }}
          >
            事案の記録がありません
          </div>
        )}
        {!loading &&
          incidents.map((inc, i) => (
            <div
              key={inc.id}
              style={{
                display: "grid",
                gridTemplateColumns: "120px 1fr 120px 100px 80px",
                borderTop: i > 0 ? `1px solid ${T.line}` : "none",
                fontSize: 12.5,
                alignItems: "center",
              }}
            >
              <div
                style={{
                  padding: "10px 12px",
                  fontFamily: T.mono,
                  color: T.ink3,
                  fontSize: 12,
                }}
              >
                {inc.incident_date}
              </div>
              <div style={{ padding: "10px 12px" }}>
                <div style={{ fontWeight: 600, marginBottom: 2 }}>
                  {inc.title}
                </div>
                <div
                  style={{
                    color: T.ink3,
                    fontSize: 11.5,
                    overflow: "hidden",
                    textOverflow: "ellipsis",
                    whiteSpace: "nowrap",
                    maxWidth: 340,
                  }}
                >
                  {inc.body}
                </div>
              </div>
              <div
                style={{
                  padding: "10px 12px",
                  fontSize: 11,
                  fontFamily: T.mono,
                  color: T.ink3,
                }}
              >
                {inc.created_at ? inc.created_at.slice(0, 10) : "—"}
              </div>
              <div
                style={{
                  padding: "10px 12px",
                  fontSize: 12,
                  color: T.ink3,
                  display: "flex",
                  flexWrap: "wrap",
                  gap: 4,
                  alignItems: "center",
                }}
              >
                {inc.involved_students && inc.involved_students.length > 0
                  ? inc.involved_students.map((s) => (
                      <button
                        key={s.id}
                        onClick={() =>
                          setProfileTarget({ id: s.id, name: s.name })
                        }
                        title="個人データを表示"
                        style={{
                          padding: "2px 8px",
                          fontSize: 11.5,
                          fontFamily: "inherit",
                          color: T.cobalt,
                          background: T.surfaceAlt,
                          border: `1px solid ${T.lineStrong}`,
                          borderRadius: 999,
                          cursor: "pointer",
                        }}
                      >
                        {s.name}
                      </button>
                    ))
                  : `${(inc.involved_student_ids || []).length}名`}
              </div>
              <div
                style={{
                  padding: "10px 8px",
                  display: "flex",
                  gap: 4,
                }}
              >
                <button
                  onClick={() => openEdit(inc)}
                  style={{
                    padding: "4px 10px",
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
                  編集
                </button>
                <button
                  onClick={() => setConfirmDelete(inc)}
                  style={{
                    padding: "4px 10px",
                    fontSize: 11,
                    fontWeight: 700,
                    background: "transparent",
                    color: T.danger,
                    border: `1px solid ${T.dangerBorder}`,
                    borderRadius: 6,
                    cursor: "pointer",
                    fontFamily: "inherit",
                  }}
                >
                  削除
                </button>
              </div>
            </div>
          ))}
      </div>

      {/* 录入 / 编辑表单 modal */}
      {showForm && (
        <div
          onClick={closeForm}
          style={{
            position: "fixed",
            inset: 0,
            background: "rgba(20,23,31,.52)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            zIndex: 300,
          }}
        >
          <div
            onClick={(e) => e.stopPropagation()}
            style={{
              width: 600,
              maxHeight: "88vh",
              background: T.surface,
              borderRadius: 14,
              boxShadow: T.shadowModal,
              overflow: "auto",
              padding: "24px 28px",
            }}
          >
            <div
              style={{
                fontSize: 17,
                fontWeight: 700,
                marginBottom: 18,
              }}
            >
              {editTarget ? "事案を編集" : "事案を登録"}
            </div>
            <div style={{ marginBottom: 14 }}>
              <div
                style={{
                  fontSize: 11,
                  color: T.ink3,
                  marginBottom: 4,
                }}
              >
                タイトル
              </div>
              <input
                value={fTitle}
                onChange={(e) => setFTitle(e.target.value)}
                placeholder="事案のタイトル（最大 200 文字）"
                style={{
                  width: "100%",
                  padding: "9px 12px",
                  border: `1px solid ${T.lineStrong}`,
                  borderRadius: 8,
                  fontFamily: "inherit",
                  fontSize: 13,
                  background: T.surface,
                  boxSizing: "border-box",
                }}
              />
            </div>
            <div style={{ marginBottom: 14 }}>
              <div
                style={{
                  fontSize: 11,
                  color: T.ink3,
                  marginBottom: 4,
                }}
              >
                発生日
              </div>
              <input
                type="date"
                value={fDate}
                onChange={(e) => setFDate(e.target.value)}
                style={{
                  width: "100%",
                  padding: "9px 12px",
                  border: `1px solid ${T.lineStrong}`,
                  borderRadius: 8,
                  fontFamily: "inherit",
                  fontSize: 13,
                  background: T.surface,
                  boxSizing: "border-box",
                }}
              />
            </div>
            <div style={{ marginBottom: 14 }}>
              <div
                style={{
                  fontSize: 11,
                  color: T.ink3,
                  marginBottom: 4,
                }}
              >
                内容
              </div>
              <textarea
                value={fBody}
                onChange={(e) => setFBody(e.target.value)}
                rows={6}
                placeholder="事案の詳細内容を記入（最大 100000 文字）"
                style={{
                  width: "100%",
                  padding: "9px 12px",
                  border: `1px solid ${T.lineStrong}`,
                  borderRadius: 8,
                  fontFamily: "inherit",
                  fontSize: 13,
                  background: T.surface,
                  resize: "vertical",
                  boxSizing: "border-box",
                }}
              />
            </div>
            <div style={{ marginBottom: 18 }}>
              <div
                style={{
                  fontSize: 11,
                  color: T.ink3,
                  marginBottom: 4,
                }}
              >
                関係学生（任意・複数選択可）
              </div>
              <StudentMultiSelect
                selected={fStudents}
                onChange={setFStudents}
                authToken={authToken}
              />
              <div style={{ fontSize: 11, color: T.ink3, marginTop: 4 }}>
                ※
                クリックで一覧を開き、名前・部屋番号・学籍番号で検索して選択できます
              </div>
            </div>
            {fError && (
              <div
                style={{
                  color: T.danger,
                  fontSize: 12,
                  marginBottom: 12,
                }}
              >
                ⚠️ {fError}
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
                onClick={closeForm}
                style={{
                  padding: "9px 18px",
                  background: "transparent",
                  color: T.ink,
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
                onClick={submitForm}
                disabled={fSubmitting}
                style={{
                  padding: "9px 22px",
                  background: T.cobalt,
                  color: "#fff",
                  border: "none",
                  borderRadius: 8,
                  fontFamily: "inherit",
                  fontSize: 13,
                  fontWeight: 700,
                  cursor: fSubmitting ? "not-allowed" : "pointer",
                  opacity: fSubmitting ? 0.7 : 1,
                }}
              >
                {fSubmitting ? "保存中…" : editTarget ? "更新" : "登録"}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* 软删除确认 modal */}
      {confirmDelete && (
        <ConfirmModal
          title="事案を削除"
          desc={`「${confirmDelete.title}」を削除します。この操作は取り消せません（論理削除）。`}
          danger
          confirmLabel="削除"
          onCancel={() => setConfirmDelete(null)}
          onConfirm={() => softDelete(confirmDelete)}
        />
      )}

      {/* toast */}
      {toast && (
        <div
          style={{
            position: "fixed",
            bottom: 28,
            left: "50%",
            transform: "translateX(-50%)",
            padding: "10px 20px",
            background: toast.type === "ok" ? T.ok : T.danger,
            color: "#fff",
            borderRadius: 8,
            fontSize: 13,
            fontWeight: 600,
            zIndex: 999,
            whiteSpace: "nowrap",
          }}
        >
          {toast.msg}
        </div>
      )}
      {/* 杭田 2026-06-04 五-6: 涉及学生姓名点击 → 个人档案弹窗 */}
      {profileTarget && (
        <StudentProfileModal
          studentId={profileTarget.id}
          studentName={profileTarget.name}
          authToken={authToken}
          onClose={() => setProfileTarget(null)}
        />
      )}
    </div>
  );
}

// 学生多选选择器 —— 替代原「逗号分隔 UUID 手输」。
// 点击触发框 → 就地展开（搜索框 + 学生列表），点行勾选 / 取消，选中显示为可删 chip。
// 不用浮层（position:absolute），避免被表单 modal 的 overflow:auto 裁掉。
function StudentMultiSelect({
  selected,
  onChange,
  authToken,
}: {
  selected: { id: string; name: string; sub?: string }[];
  onChange: (next: { id: string; name: string; sub?: string }[]) => void;
  authToken: string;
}) {
  const T = RYO;
  const [open, setOpen] = React.useState(false);
  const [query, setQuery] = React.useState("");
  const [results, setResults] = React.useState<
    { id: string; name: string; sub: string }[]
  >([]);
  const [loading, setLoading] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);
  const boxRef = React.useRef<HTMLDivElement>(null);

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

  // 展开 / 改搜索词 → 拉学生（200ms 防抖，避免每键一次请求）
  React.useEffect(() => {
    if (!open || !authToken) return;
    let cancelled = false;
    setLoading(true);
    const timer = setTimeout(() => {
      api
        .listStudents(query.trim() ? { q: query.trim() } : undefined, authToken)
        .then((res) => {
          if (cancelled) return;
          setResults(
            (res.items || []).map((s) => ({
              id: s.id,
              name: s.name,
              sub: `${s.room_no}号室 · ${s.student_no}`,
            })),
          );
          setError(null);
          setLoading(false);
        })
        .catch((e) => {
          if (cancelled) return;
          setError(e.message || "学生リストの取得に失敗しました");
          setResults([]);
          setLoading(false);
        });
    }, 200);
    return () => {
      cancelled = true;
      clearTimeout(timer);
    };
  }, [open, query, authToken]);

  const isSelected = (id: string) => selected.some((s) => s.id === id);
  const toggle = (s: { id: string; name: string; sub?: string }) => {
    if (isSelected(s.id)) {
      onChange(selected.filter((x) => x.id !== s.id));
    } else {
      onChange([...selected, { id: s.id, name: s.name, sub: s.sub }]);
    }
  };

  return (
    <div ref={boxRef}>
      {/* 触发框：显示选中 chip + 展开箭头 */}
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
        {selected.length === 0 && (
          <span style={{ fontSize: 13, color: T.ink3 }}>
            学生を選択（クリックで一覧）
          </span>
        )}
        {selected.map((s) => (
          <span
            key={s.id}
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
            {!loading && !error && results.length === 0 && (
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
              results.map((s) => {
                const on = isSelected(s.id);
                return (
                  <div
                    key={s.id}
                    onClick={() => toggle(s)}
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
                    <span style={{ flex: 1, color: T.ink }}>{s.name}</span>
                    <span
                      style={{
                        fontSize: 11,
                        color: T.ink3,
                        fontFamily: T.mono,
                      }}
                    >
                      {s.sub}
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
