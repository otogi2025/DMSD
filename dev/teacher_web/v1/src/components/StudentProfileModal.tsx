import React from "react";
import { RYO, S } from "../theme";
import { api } from "../api/client";
import type {
  StudentProfile,
  ProfileApplicationEntry,
  ProfileStudyCheckinEntry,
  ProfileRollCallEntry,
  ProfileDemeritEntry,
} from "../api/types";

// 源 index.html 26837-27691（components/accounts.jsx 块）。界面原样搬，
// 仅作用域引用改写：window.RYO→RYO / window.tomoshibiApi→api。
// window.open / window.location 是浏览器全局，原样保留。

// 屏内提示条（toast）的形状
type Toast = { type: "ok" | "danger"; msg: string };

// web#24：日本时间（JST）今日 YYYY-MM-DD — 不用 toISOString（UTC，早 0–8 点会变成昨天）
function todayJstDate(): string {
  return new Date().toLocaleDateString("en-CA", { timeZone: "Asia/Tokyo" });
}

// web#126：学生账号状态 → 日语（对齐 AccountsPage active→正常；未知回退原文）
function studentStatusJa(status: string): string {
  return (
    (
      {
        active: "正常",
        locked: "ロック",
        paused: "休止",
        graduated: "卒業",
        transferred: "転学",
      } as Record<string, string>
    )[status] || status
  );
}

// web#127：gender 显式分支，空/其它显示「—」
function genderJa(gender: string): string {
  if (gender === "male") return "男";
  if (gender === "female") return "女";
  return "—";
}

export function StudentProfileModal({
  studentId,
  studentName,
  authToken,
  onClose,
}: {
  studentId: string;
  studentName: string;
  authToken: string;
  onClose: () => void;
}) {
  const T = RYO;
  const [data, setData] = React.useState<StudentProfile | null>(null);
  const [loading, setLoading] = React.useState(true);
  const [error, setError] = React.useState<string | null>(null);
  const [tab, setTab] = React.useState("basic");
  // 指導 tab — 录入表单开关
  const [showGuidanceForm, setShowGuidanceForm] = React.useState(false);
  const [gContent, setGContent] = React.useState("");
  const [gCategory, setGCategory] = React.useState("");
  // web#24：「指導日」默认用日本时间今天
  const [gDate, setGDate] = React.useState(todayJstDate);
  const [gConfidential, setGConfidential] = React.useState(true);
  const [gSubmitting, setGSubmitting] = React.useState(false);
  const [gError, setGError] = React.useState<string | null>(null);
  const [toast, setToast] = React.useState<Toast | null>(null);

  // web#26：竞态守卫 — 快切学生时丢弃过期响应，避免标题已换、内容仍是上一人
  React.useEffect(() => {
    if (!authToken || !studentId) return;
    let cancelled = false;
    setLoading(true);
    setError(null);
    api
      .getStudentProfile(studentId, authToken)
      .then((d) => {
        if (cancelled) return;
        setData(d);
        setLoading(false);
      })
      .catch((e) => {
        if (cancelled) return;
        setError(e.message || "個人データの取得に失敗しました");
        setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [studentId, authToken]);

  React.useEffect(() => {
    if (toast) {
      const id = setTimeout(() => setToast(null), 3500);
      return () => clearTimeout(id);
    }
  }, [toast]);

  const submitGuidance = () => {
    if (!gContent.trim()) {
      setGError("内容を入力してください");
      return;
    }
    setGSubmitting(true);
    setGError(null);
    api
      .createGuidance(
        studentId,
        {
          student_id: studentId,
          content: gContent.trim(),
          category: gCategory.trim() || undefined,
          guidance_date: gDate,
          confidential: gConfidential,
        },
        authToken,
      )
      .then((rec) => {
        // 把新记录追加到 data.guidance_records 头部
        setData((prev) =>
          prev
            ? {
                ...prev,
                guidance_records: [rec, ...(prev.guidance_records || [])],
              }
            : prev,
        );
        setGContent("");
        setGCategory("");
        setGDate(todayJstDate()); // web#24：与初始默认共用 JST helper
        setGConfidential(true);
        setShowGuidanceForm(false);
        setGSubmitting(false);
        setToast({ type: "ok", msg: "指導記録を登録しました" });
      })
      .catch((e) => {
        setGError(e.message || "登録失敗");
        setGSubmitting(false);
      });
  };

  const TABS = [
    ["basic", "基本情報"],
    ["applications", "出寮届"],
    ["study", "夜学習出席"],
    ["online", "オンライン学習"],
    ["rollcall", "点呼"],
    ["guidance", "指導履歴"],
    ["demerit", "減点"],
  ];

  const s = data && data.student;

  return (
    <div
      onClick={onClose}
      style={{
        ...S.backdrop,
        zIndex: 300,
      }}
    >
      <div
        onClick={(e) => e.stopPropagation()}
        className="t-scale-in"
        style={{
          ...S.modal,
          width: 740,
          maxHeight: "88vh",
          display: "flex",
          flexDirection: "column",
          overflow: "hidden",
        }}
      >
        {/* 头部 */}
        <div
          style={{
            padding: "20px 24px 0",
            borderBottom: `1px solid ${T.line}`,
            flexShrink: 0,
          }}
        >
          <div
            style={{
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
              marginBottom: 14,
            }}
          >
            <div>
              <div
                style={{
                  fontSize: 11,
                  color: T.ink3,
                  letterSpacing: 2,
                  fontWeight: 600,
                }}
              >
                個人データ
              </div>
              <div style={{ fontSize: 20, fontWeight: 700, marginTop: 2 }}>
                {studentName}
                {s && (
                  <span
                    style={{
                      fontSize: 12,
                      fontWeight: 500,
                      color: T.ink3,
                      marginLeft: 10,
                      fontFamily: T.mono,
                    }}
                  >
                    {s.student_no}
                  </span>
                )}
              </div>
            </div>
            <button
              onClick={onClose}
              style={{
                background: "transparent",
                border: "none",
                fontSize: 22,
                cursor: "pointer",
                color: T.ink3,
                lineHeight: 1,
                padding: "0 4px",
              }}
            >
              ×
            </button>
          </div>
          {/* 标签栏 */}
          <div style={{ display: "flex", gap: 2 }}>
            {TABS.map(([id, label]) => (
              <button
                key={id}
                onClick={() => setTab(id)}
                style={{
                  padding: "8px 14px",
                  fontSize: 12.5,
                  fontWeight: tab === id ? 700 : 500,
                  color: tab === id ? T.cobaltDeep : T.ink3,
                  background: "transparent",
                  border: "none",
                  borderBottom:
                    tab === id
                      ? `2px solid ${T.cobalt}`
                      : "2px solid transparent",
                  fontFamily: "inherit",
                  cursor: "pointer",
                  marginBottom: -1,
                }}
              >
                {label}
              </button>
            ))}
          </div>
        </div>

        {/* 内容区 */}
        <div style={{ flex: 1, overflowY: "auto", padding: "20px 24px" }}>
          {loading && (
            <div style={{ textAlign: "center", color: T.ink3, padding: 40 }}>
              読み込み中…
            </div>
          )}
          {error && (
            <div
              style={{
                padding: "10px 14px",
                background: T.dangerSoft,
                border: `1px solid ${T.dangerBorder}`,
                borderRadius: 10,
                color: T.danger,
                fontSize: 13,
              }}
            >
              ⚠️ {error}
            </div>
          )}
          {!loading && !error && data && s && (
            <>
              {/* 基本情報 tab */}
              {tab === "basic" && (
                <div
                  style={{
                    display: "grid",
                    gridTemplateColumns: "1fr 1fr",
                    gap: "10px 24px",
                  }}
                >
                  {[
                    ["学籍番号", s.student_no],
                    ["氏名", s.name],
                    ["ふりがな", s.name_kana || "—"],
                    ["性別", genderJa(s.gender)],
                    ["学年", s.grade_code],
                    ["組", s.class_code],
                    ["出席番号", s.seat_no],
                    ["部屋番号", s.room_no],
                    ["寮", `${s.dorm_unit}寮`],
                    ["留学生", s.is_overseas ? "はい" : "いいえ"],
                    ["メール", s.email || "—"],
                    ["電話", s.phone || "—"],
                    ["状態", studentStatusJa(s.status)],
                    [
                      "登録日時",
                      s.registered_at ? s.registered_at.slice(0, 10) : "—",
                    ],
                  ].map(([k, v]) => (
                    <div key={k}>
                      <div
                        style={{
                          fontSize: 10,
                          color: T.ink3,
                          fontWeight: 600,
                          marginBottom: 2,
                        }}
                      >
                        {k}
                      </div>
                      <div style={{ fontSize: 13.5, fontWeight: 500 }}>{v}</div>
                    </div>
                  ))}
                </div>
              )}

              {/* 出寮届 tab */}
              {tab === "applications" && (
                <ProfileList
                  items={data.applications}
                  emptyMsg="出寮届の記録がありません"
                  cols={["種別", "外出日", "帰寮日", "状態", "申請日"]}
                  render={(a: ProfileApplicationEntry) => [
                    a.kind,
                    a.leave_date,
                    a.return_date,
                    a.status,
                    a.submitted_at ? a.submitted_at.slice(0, 10) : "—",
                  ]}
                />
              )}

              {/* 夜学習出席 tab */}
              {tab === "study" && (
                <ProfileList
                  items={data.study_checkins}
                  emptyMsg="夜学習出席の記録がありません"
                  cols={["対象日", "状態", "チェックイン"]}
                  render={(sc: ProfileStudyCheckinEntry) => [
                    sc.target_date,
                    sc.status,
                    sc.checked_at
                      ? sc.checked_at.slice(0, 16).replace("T", " ")
                      : "—",
                  ]}
                />
              )}

              {/* 点呼 tab — 杭田 2026-06-04 五-5: 朝点呼 / 夜点呼 分两块显示 */}
              {tab === "rollcall" &&
                (() => {
                  const rcCols = ["状態", "判定ソース", "チェックイン日時"];
                  const rcRender = (r: ProfileRollCallEntry) => [
                    r.base_status,
                    r.status_source,
                    r.checked_in_at
                      ? r.checked_in_at.slice(0, 16).replace("T", " ")
                      : "—",
                  ];
                  const all = data.rollcall_events || [];
                  const morning = all.filter(
                    (r) => r.session_type === "morning",
                  );
                  const evening = all.filter(
                    (r) => r.session_type === "evening",
                  );
                  const subhead = {
                    fontSize: 12,
                    fontWeight: 700,
                    color: T.ink2,
                    margin: "4px 0 8px",
                  };
                  return (
                    <div>
                      <div style={subhead}>朝点呼</div>
                      <ProfileList
                        items={morning}
                        emptyMsg="朝点呼の記録がありません"
                        cols={rcCols}
                        render={rcRender}
                      />
                      <div style={{ ...subhead, marginTop: 18 }}>夜点呼</div>
                      <ProfileList
                        items={evening}
                        emptyMsg="夜点呼の記録がありません"
                        cols={rcCols}
                        render={rcRender}
                      />
                    </div>
                  );
                })()}

              {/* 指導履歴 tab */}
              {tab === "guidance" && (
                <div>
                  {/* web#25：权限不足时后端可能省略/置空 guidance_records，与 online tab 同样兜底 */}
                  {(data.guidance_records || []).length === 0 &&
                    !showGuidanceForm && (
                      <div
                        style={{
                          color: T.ink3,
                          fontSize: 13,
                          marginBottom: 16,
                        }}
                      >
                        指導履歴がありません（または権限なし）
                      </div>
                    )}
                  {(data.guidance_records || []).length > 0 && (
                    <div style={{ marginBottom: 16 }}>
                      {(data.guidance_records || []).map((gr, gi) => (
                        <div
                          key={gr.id}
                          className="t-fade-up"
                          style={{
                            padding: "12px 14px",
                            marginBottom: 8,
                            background: T.surfaceAlt,
                            borderRadius: 10,
                            border: `1px solid ${T.line}`,
                            ...(gi < 12
                              ? { animationDelay: `${gi * 40}ms` }
                              : null),
                          }}
                        >
                          <div
                            style={{
                              display: "flex",
                              justifyContent: "space-between",
                              marginBottom: 6,
                            }}
                          >
                            <span
                              style={{
                                fontSize: 12,
                                fontWeight: 700,
                                color: T.ink2,
                              }}
                            >
                              {gr.guidance_date}
                              {gr.category && (
                                <span
                                  style={{
                                    ...S.pill,
                                    marginLeft: 8,
                                    padding: "1px 6px",
                                    background: T.cobaltSoft,
                                    color: T.cobaltDeep,
                                    fontSize: 11,
                                  }}
                                >
                                  {gr.category}
                                </span>
                              )}
                            </span>
                            {gr.confidential && (
                              <span
                                style={{
                                  fontSize: 10,
                                  color: T.warn,
                                  fontWeight: 700,
                                }}
                              >
                                🔒 機密
                              </span>
                            )}
                          </div>
                          <div
                            style={{
                              fontSize: 13,
                              lineHeight: 1.6,
                              whiteSpace: "pre-wrap",
                            }}
                          >
                            {gr.content}
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                  {/* 录入表单 */}
                  {showGuidanceForm ? (
                    <div
                      style={{
                        padding: "16px",
                        background: T.surfaceAlt,
                        borderRadius: 12,
                        border: `1px solid ${T.line}`,
                      }}
                    >
                      <div
                        style={{
                          fontSize: 13,
                          fontWeight: 700,
                          marginBottom: 12,
                        }}
                      >
                        指導記録を登録
                      </div>
                      <div
                        style={{
                          display: "grid",
                          gridTemplateColumns: "1fr 1fr",
                          gap: 10,
                          marginBottom: 10,
                        }}
                      >
                        <div>
                          <div
                            style={{
                              fontSize: 11,
                              color: T.ink3,
                              marginBottom: 4,
                            }}
                          >
                            指導日
                          </div>
                          <input
                            type="date"
                            value={gDate}
                            onChange={(e) => setGDate(e.target.value)}
                            className="t-input"
                            style={{
                              ...S.input,
                              width: "100%",
                              padding: "8px 10px",
                              border: `1px solid ${T.lineStrong}`,
                              boxSizing: "border-box",
                            }}
                          />
                        </div>
                        <div>
                          <div
                            style={{
                              fontSize: 11,
                              color: T.ink3,
                              marginBottom: 4,
                            }}
                          >
                            カテゴリ（任意）
                          </div>
                          <input
                            value={gCategory}
                            onChange={(e) => setGCategory(e.target.value)}
                            placeholder="例：生活態度、門限違反"
                            className="t-input"
                            style={{
                              ...S.input,
                              width: "100%",
                              padding: "8px 10px",
                              border: `1px solid ${T.lineStrong}`,
                              boxSizing: "border-box",
                            }}
                          />
                        </div>
                      </div>
                      <div style={{ marginBottom: 10 }}>
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
                          value={gContent}
                          onChange={(e) => setGContent(e.target.value)}
                          rows={4}
                          placeholder="指導内容を記入してください（最大 4000 文字）"
                          className="t-input"
                          style={{
                            ...S.input,
                            width: "100%",
                            padding: "8px 10px",
                            border: `1px solid ${T.lineStrong}`,
                            resize: "vertical",
                            boxSizing: "border-box",
                          }}
                        />
                      </div>
                      <label
                        style={{
                          display: "flex",
                          alignItems: "center",
                          gap: 6,
                          fontSize: 12.5,
                          cursor: "pointer",
                          marginBottom: 12,
                        }}
                      >
                        <input
                          type="checkbox"
                          checked={gConfidential}
                          onChange={(e) => setGConfidential(e.target.checked)}
                        />
                        機密扱い（寮生本人に非表示）
                      </label>
                      {gError && (
                        <div
                          style={{
                            color: T.danger,
                            fontSize: 12,
                            marginBottom: 8,
                          }}
                        >
                          ⚠️ {gError}
                        </div>
                      )}
                      <div style={{ display: "flex", gap: 8 }}>
                        <button
                          onClick={submitGuidance}
                          disabled={gSubmitting}
                          className="t-btn"
                          style={{
                            ...S.btnPrimary,
                            padding: "9px 20px",
                            cursor: gSubmitting ? "not-allowed" : "pointer",
                            opacity: gSubmitting ? 0.7 : 1,
                          }}
                        >
                          {gSubmitting ? "登録中…" : "登録"}
                        </button>
                        <button
                          onClick={() => {
                            setShowGuidanceForm(false);
                            setGError(null);
                          }}
                          className="t-btn"
                          style={{
                            ...S.btnGhost,
                            padding: "9px 18px",
                          }}
                        >
                          キャンセル
                        </button>
                      </div>
                    </div>
                  ) : (
                    <button
                      onClick={() => setShowGuidanceForm(true)}
                      className="t-btn"
                      style={{
                        ...S.btnPrimary,
                        padding: "9px 18px",
                      }}
                    >
                      ＋ 指導記録を登録
                    </button>
                  )}
                </div>
              )}

              {/* 扣分 tab */}
              {tab === "demerit" && (
                <ProfileList
                  items={data.demerit_events}
                  emptyMsg="減点の記録がありません"
                  cols={["種別", "ポイント", "理由", "月", "登録日"]}
                  render={(d: ProfileDemeritEntry) => [
                    d.source_type,
                    d.points,
                    d.reason,
                    d.month,
                    d.created_at ? d.created_at.slice(0, 10) : "—",
                  ]}
                />
              )}

              {/* 在线学习申请 tab — 含契約書（合同）查看 */}
              {tab === "online" && (
                <div>
                  {(!data.study_online_requests ||
                    data.study_online_requests.length === 0) && (
                    <div style={{ color: T.ink3, fontSize: 13 }}>
                      オンライン学習申請がありません
                    </div>
                  )}
                  {data.study_online_requests &&
                    data.study_online_requests.map((so, soi) => (
                      <div
                        key={so.id}
                        className="t-fade-up"
                        style={{
                          padding: "12px 14px",
                          marginBottom: 8,
                          background: T.surfaceAlt,
                          borderRadius: 10,
                          border: `1px solid ${T.line}`,
                          ...(soi < 12
                            ? { animationDelay: `${soi * 40}ms` }
                            : null),
                        }}
                      >
                        <div
                          style={{
                            display: "flex",
                            justifyContent: "space-between",
                            marginBottom: 8,
                          }}
                        >
                          <span
                            style={{
                              fontSize: 12,
                              fontWeight: 700,
                              color: T.ink2,
                            }}
                          >
                            {so.period_from} 〜 {so.period_to}
                          </span>
                          <span style={{ fontSize: 11, color: T.ink3 }}>
                            {so.status === "approved"
                              ? "許可"
                              : so.status === "rejected"
                                ? "却下"
                                : so.status === "revoked"
                                  ? "取消"
                                  : "審査中"}
                          </span>
                        </div>
                        {so.contract_file_name ? (
                          <button
                            onClick={async () => {
                              // 先在点击的同步时机开空窗口，再 await 取文件 —
                              // 否则 await 后再 window.open 会被浏览器当非用户操作拦截
                              const win = window.open("", "_blank");
                              try {
                                const blob = await api.downloadOnlineContract(
                                  so.id,
                                  authToken,
                                );
                                const url = URL.createObjectURL(blob);
                                if (win) {
                                  win.location = url;
                                } else {
                                  // 弹窗被拦 → 退化成当前页跳转
                                  window.location.href = url;
                                }
                                setTimeout(
                                  () => URL.revokeObjectURL(url),
                                  60000,
                                );
                              } catch (e) {
                                if (win) win.close();
                                setToast({
                                  type: "danger",
                                  msg: "契約書の取得に失敗しました",
                                });
                              }
                            }}
                            className="t-btn"
                            style={{
                              ...S.btnSmall,
                              padding: "6px 12px",
                              background: T.cobaltSoft,
                              color: T.cobaltDeep,
                              border: "none",
                              fontWeight: 700,
                            }}
                          >
                            📎 契約書を見る（{so.contract_file_name}）
                          </button>
                        ) : (
                          <span style={{ fontSize: 12, color: T.ink3 }}>
                            契約書の添付なし
                          </span>
                        )}
                      </div>
                    ))}
                </div>
              )}
            </>
          )}
        </div>

        {/* 提示条 */}
        {toast && (
          <div
            style={{
              position: "absolute",
              bottom: 20,
              left: "50%",
              transform: "translateX(-50%)",
              padding: "10px 20px",
              background: toast.type === "ok" ? T.ok : T.danger,
              color: "#fff",
              borderRadius: 10,
              fontSize: 13,
              fontWeight: 600,
              pointerEvents: "none",
              whiteSpace: "nowrap",
            }}
          >
            {toast.msg}
          </div>
        )}
      </div>
    </div>
  );
}

// ProfileList — profile modal 内的通用表格（私有子组件，不 export）
function ProfileList<T extends { id?: string | number }>({
  items,
  emptyMsg,
  cols,
  render,
}: {
  items: T[];
  emptyMsg: string;
  cols: string[];
  render: (item: T) => React.ReactNode[];
}) {
  const TH = RYO;
  if (!items || items.length === 0) {
    return (
      <div style={{ color: TH.ink3, fontSize: 13, padding: "20px 0" }}>
        {emptyMsg}
      </div>
    );
  }
  return (
    <div
      style={{
        ...S.card,
        overflow: "hidden",
      }}
    >
      {/* 表头 padding 比 S.tableHead 小，只换颜色不套配方 */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: `repeat(${cols.length}, 1fr)`,
          background: TH.surfaceAlt,
          fontSize: 11,
          color: TH.ink3,
          fontWeight: 600,
          letterSpacing: 1,
          borderBottom: `1px solid ${TH.line}`,
        }}
      >
        {cols.map((c) => (
          <div key={c} style={{ padding: "8px 12px" }}>
            {c}
          </div>
        ))}
      </div>
      {items.map((item, i) => (
        <div
          key={item.id || i}
          className="t-row"
          style={{
            display: "grid",
            gridTemplateColumns: `repeat(${cols.length}, 1fr)`,
            borderTop: i > 0 ? `1px solid ${TH.line}` : "none",
            fontSize: 12.5,
          }}
        >
          {render(item).map((v, j) => (
            <div key={j} style={{ padding: "8px 12px", color: TH.ink }}>
              {v == null ? "—" : String(v)}
            </div>
          ))}
        </div>
      ))}
    </div>
  );
}
