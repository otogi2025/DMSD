import React from "react";
import { RYO, S } from "../theme";
import { api } from "../api/client";
import type { OutingOut, OutingStatus } from "../api/types";

// 外出申请管理页（UI「外出申請」）— itsuki 2026-07-22 拍板的「事后确认制」老师侧。
//
// 「外出」= 当天回寮的短时间外出（去车站前、买东西），跟「出寮届」（过夜、多级审批、
// 走 applications 接口的那套）是两套完全不同的东西，别混。
//
// 事后确认制的三条语义（决定这一页长什么样）：
//   1. 学生提交那一刻外出就已经生效，可以直接出门 —— 老师不是放行闸
//   2. 老师点「確認」= 事后留一条「我看过了」的记录，点之前学生早就出门了
//   3. 老师仍可「却下」（现实中很少用）：只给学生发通知 + 留记录，
//      不要求学生立刻回寮；却下理由可以不填
//
// 后端契约（dev/backend/v1/app/routers/outings.py）：
//   GET   /outings/for-me?status=  四态筛选（pending/approved/rejected/withdrawn），提交时刻倒序
//   PATCH /outings/{id}/confirm    无请求体
//   PATCH /outings/{id}/reject     请求体 {reason} 可选、整体也可省略
//   已处理过的再点 → 409 OUTING_NOT_PENDING（两个老师同时点会撞到）
//
// ⚠️ confirmed_by_teacher_id / confirmed_by_name / confirmed_at 是「処理した先生 / 処理時刻」：
//    status=approved 时是确认者、status=rejected 时是却下者，显示文案必须按 status 分支。

// 后端 time 字段是 "HH:MM:SS"，界面只显示到分
function hhmm(t: string | null | undefined): string {
  if (!t) return "";
  return t.length >= 5 ? t.slice(0, 5) : t;
}

// ISO 时刻 → JST「MM/DD HH:MM」（跟通知中心 formatTime 同一口径，钉死 24 小时制）
function formatDateTime(iso: string | null | undefined): string {
  if (!iso) return "";
  const d = new Date(iso);
  if (isNaN(d.getTime())) return iso;
  return d.toLocaleString("ja-JP", {
    timeZone: "Asia/Tokyo",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
    hour12: false,
  });
}

// 状态 → [标签, 文字色, 底色, 边框色]
function statusMeta(
  s: OutingStatus,
  T: typeof RYO,
): [string, string, string, string] {
  if (s === "pending") return ["確認待ち", T.warn, T.warnSoft, T.warnBorder];
  if (s === "approved") return ["確認済", T.ok, T.okSoft, T.okBorder];
  if (s === "rejected")
    return ["却下済", T.danger, T.dangerSoft, T.dangerBorder];
  return ["取消済", T.ink3, T.graySoft, T.grayBorder];
}

// 「処理した先生」那一栏的说明词 —— confirmed_* 三个字段确认和却下共用，
// 所以文案要按 status 分支，不能一律写「確認」
function actionLabel(s: OutingStatus): string {
  if (s === "approved") return "確認";
  if (s === "rejected") return "却下";
  return "";
}

const FILTERS: Array<[OutingStatus, string]> = [
  ["pending", "確認待ち"],
  ["approved", "確認済"],
  ["rejected", "却下済"],
  ["withdrawn", "取消済"],
];

// 表格列宽 —— 表头和数据行共用同一个字符串，改列宽只改这一处
const GRID = "170px 110px 1fr 130px 1fr 96px 150px";

export function OutingsPage({ authToken }: { authToken: string | null }) {
  const T = RYO;
  const [filter, setFilter] = React.useState<OutingStatus>("pending");
  const [list, setList] = React.useState<OutingOut[] | null>(null);
  const [loading, setLoading] = React.useState(false);
  const [err, setErr] = React.useState("");
  // 点开详情弹窗的那一条；null = 弹窗关闭
  const [selected, setSelected] = React.useState<OutingOut | null>(null);
  const [rejectReason, setRejectReason] = React.useState("");
  // 处理中标记（按 outing id）—— 防慢网下重复点「確認」/「却下」
  const [acting, setActing] = React.useState<Record<string, boolean>>({});

  const refetch = React.useCallback(async () => {
    if (!authToken) return;
    setLoading(true);
    setErr("");
    try {
      const data = await api.outingsForMe(authToken, filter);
      setList(data || []);
    } catch (e) {
      const ex = e as { status?: number };
      if (ex && ex.status === 403) {
        setErr("このページは「申請の閲覧」権限が必要です");
      } else if (ex && ex.status) {
        setErr(`サーバーエラー (${ex.status})`);
      } else {
        setErr("サーバーに接続できません。しばらくしてから再度お試しください");
      }
      setList([]);
    } finally {
      setLoading(false);
    }
  }, [authToken, filter]);

  React.useEffect(() => {
    refetch();
  }, [refetch]);

  // 打开 / 切换详情时把上一条残留的却下理由清掉，防止串到别人的申请上
  const openDetail = (o: OutingOut) => {
    setSelected(o);
    setRejectReason("");
  };

  const closeDetail = () => {
    setSelected(null);
    setRejectReason("");
  };

  // 確認 / 却下 共用一条处理路径：两者的成功、失败、409 撞车处理完全同构
  const doDecide = async (o: OutingOut, decision: "confirm" | "reject") => {
    if (!authToken || acting[o.id]) return;
    setActing((m) => ({ ...m, [o.id]: true }));
    try {
      if (decision === "confirm") {
        await api.confirmOuting(o.id, authToken);
      } else {
        // 却下理由不强制 —— 空串按「不填」传 undefined，别把空字符串写进记录
        await api.rejectOuting(
          o.id,
          rejectReason.trim() || undefined,
          authToken,
        );
      }
      closeDetail();
      await refetch();
    } catch (e) {
      const ex = e as { status?: number };
      if (ex && ex.status === 409) {
        // 409 OUTING_NOT_PENDING —— 别的老师抢先处理了同一条。
        // 不是老师操作错误，所以说明「已经被处理过」并把列表刷成最新，不留在过期弹窗里。
        setErr("他の先生が既に処理しました。最新の状態に更新しました");
        closeDetail();
        await refetch();
      } else {
        setErr(
          `${decision === "confirm" ? "確認" : "却下"}に失敗しました (${
            (ex && ex.status) || "network"
          })`,
        );
      }
    } finally {
      setActing((m) => ({ ...m, [o.id]: false }));
    }
  };

  const rows = list || [];

  return (
    <div style={{ padding: "28px 32px 48px" }}>
      <div
        style={{
          display: "flex",
          alignItems: "baseline",
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
            外出申請 &gt; {FILTERS.find(([v]) => v === filter)?.[1]}
          </div>
          <h1
            style={{
              fontSize: 24,
              fontWeight: 700,
              margin: "4px 0 0",
              letterSpacing: -0.3,
            }}
          >
            外出申請
          </h1>
        </div>
        <div style={{ display: "flex", gap: 8 }}>
          {FILTERS.map(([value, label]) => (
            <button
              key={value}
              onClick={() => setFilter(value)}
              className="t-btn"
              style={{
                padding: "8px 14px",
                background: filter === value ? T.cobalt : T.surface,
                color: filter === value ? "#fff" : T.ink2,
                border: `1px solid ${filter === value ? T.cobalt : T.lineStrong}`,
                borderRadius: 10,
                fontFamily: "inherit",
                fontSize: 12,
                fontWeight: 700,
                cursor: "pointer",
                transition: T.ease,
              }}
            >
              {label}
            </button>
          ))}
          <button
            onClick={() => refetch()}
            className="t-btn"
            style={{
              ...S.btnGhost,
              padding: "8px 14px",
              fontSize: 12,
              fontWeight: 400,
              color: T.ink2,
            }}
          >
            再読み込み
          </button>
        </div>
      </div>

      {/* 事后确认制的说明条 —— 老师最容易误解的就是「点了確認学生才能出门」，
          所以这句话必须在页面最上方常驻，不能只写在帮助文档里 */}
      <div
        style={{
          ...S.cardSoft,
          padding: "12px 16px",
          fontSize: 12.5,
          lineHeight: 1.7,
          color: T.ink2,
          marginBottom: 16,
        }}
      >
        外出申請は、寮生が提出した時点で有効になります。先生の「確認」は事後の記録であり、外出を許可するためのスイッチではありません。
        <br />
        内容に問題がある場合のみ「却下」してください（却下しても、その場で帰寮させる指示にはなりません）。
      </div>

      {err && (
        <div
          style={{
            padding: 12,
            background: T.dangerSoft,
            color: T.danger,
            border: `1px solid ${T.dangerBorder}`,
            borderRadius: 10,
            fontSize: 12,
            marginBottom: 14,
          }}
        >
          {err}
        </div>
      )}

      <div
        style={{
          ...S.card,
          overflow: "hidden",
        }}
      >
        <div
          style={{
            display: "grid",
            gridTemplateColumns: GRID,
            background: T.surfaceAlt,
            color: T.ink2,
            fontSize: 11,
            fontWeight: 600,
            letterSpacing: 1,
            borderBottom: `1px solid ${T.line}`,
          }}
        >
          {[
            "寮生",
            "外出日",
            "行き先",
            "外出～帰寮",
            "事由",
            "状態",
            "処理した先生",
          ].map((h) => (
            <div key={h} style={{ padding: "10px 14px" }}>
              {h}
            </div>
          ))}
        </div>

        {loading && rows.length === 0 && (
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

        {!loading && rows.length === 0 && (
          <div
            style={{
              padding: 40,
              textAlign: "center",
              color: T.ink3,
              fontSize: 13,
            }}
          >
            {/* 空状态文案直接复用 FILTERS 里的页签名，加页签时不用再改这里 */}
            {`${FILTERS.find(([v]) => v === filter)?.[1] ?? ""}の外出申請はありません`}
          </div>
        )}

        {rows.map((o, i) => {
          const sm = statusMeta(o.status, T);
          return (
            <div
              key={o.id}
              onClick={() => openDetail(o)}
              className="t-row"
              style={{
                display: "grid",
                gridTemplateColumns: GRID,
                borderTop: i > 0 ? `1px solid ${T.line}` : "none",
                alignItems: "center",
                fontSize: 13,
                cursor: "pointer",
              }}
            >
              <div style={{ padding: "10px 14px" }}>
                {o.student ? (
                  <>
                    <div style={{ fontWeight: 600 }}>{o.student.name}</div>
                    <div
                      style={{
                        fontSize: 11,
                        color: T.ink3,
                        fontFamily: T.mono,
                      }}
                    >
                      {o.student.student_no}
                      {o.student.room_no ? ` · ${o.student.room_no}` : ""}
                    </div>
                  </>
                ) : (
                  <span style={{ fontFamily: T.mono, fontSize: 11 }}>
                    {String(o.student_id).slice(0, 8)}…
                  </span>
                )}
              </div>
              <div
                style={{
                  padding: "10px 14px",
                  fontFamily: T.mono,
                  fontSize: 12,
                }}
              >
                {o.outing_date}
              </div>
              <div style={{ padding: "10px 14px" }}>
                {o.destination || <span style={{ color: T.ink3 }}>—</span>}
              </div>
              <div style={{ padding: "10px 14px" }}>
                <div style={{ fontFamily: T.mono, fontSize: 12 }}>
                  {o.leave_time || o.return_time
                    ? `${hhmm(o.leave_time) || "—"} 〜 ${hhmm(o.return_time) || "—"}`
                    : "—"}
                </div>
                {/* 出租车预约时刻只有填了才显示 —— 没预约的占位「タクシー なし」是噪音 */}
                {o.taxi_reservation_time && (
                  <div
                    style={{
                      fontSize: 10.5,
                      color: T.ink3,
                      marginTop: 2,
                    }}
                  >
                    タクシー {hhmm(o.taxi_reservation_time)}
                  </div>
                )}
              </div>
              <div
                style={{
                  padding: "10px 14px",
                  color: o.reason ? T.ink : T.ink3,
                  overflow: "hidden",
                  textOverflow: "ellipsis",
                  whiteSpace: "nowrap",
                }}
              >
                {o.reason || "—"}
              </div>
              <div style={{ padding: "10px 14px" }}>
                <span
                  style={{
                    ...S.pill,
                    fontSize: 11,
                    fontWeight: 700,
                    padding: "2px 8px",
                    borderRadius: 4,
                    background: sm[2],
                    color: sm[1],
                    border: `1px solid ${sm[3]}`,
                  }}
                >
                  {sm[0]}
                </span>
              </div>
              <div style={{ padding: "10px 14px" }}>
                {o.confirmed_by_name ? (
                  <>
                    <div style={{ fontSize: 12 }}>
                      {o.confirmed_by_name} 先生
                    </div>
                    <div
                      style={{
                        fontSize: 10.5,
                        color: T.ink3,
                        fontFamily: T.mono,
                      }}
                    >
                      {actionLabel(o.status)} {formatDateTime(o.confirmed_at)}
                    </div>
                  </>
                ) : (
                  <span style={{ color: T.ink3, fontSize: 12 }}>—</span>
                )}
              </div>
            </div>
          );
        })}
      </div>

      {selected && (
        <OutingDetailModal
          outing={selected}
          rejectReason={rejectReason}
          onChangeRejectReason={setRejectReason}
          busy={!!acting[selected.id]}
          onClose={closeDetail}
          onConfirm={() => doDecide(selected, "confirm")}
          onReject={() => doDecide(selected, "reject")}
        />
      )}
    </div>
  );
}

// 详情弹窗 —— 遮罩点空白关闭、内容区 stopPropagation，跟 OutstayDetailModal 同款结构
function OutingDetailModal({
  outing,
  rejectReason,
  onChangeRejectReason,
  busy,
  onClose,
  onConfirm,
  onReject,
}: {
  outing: OutingOut;
  rejectReason: string;
  onChangeRejectReason: (v: string) => void;
  busy: boolean;
  onClose: () => void;
  onConfirm: () => void;
  onReject: () => void;
}) {
  const T = RYO;
  const sm = statusMeta(outing.status, T);
  const isPending = outing.status === "pending";

  // 一行「标签 : 值」—— 弹窗里 7 处复用
  const Field = ({
    label,
    value,
    mono,
  }: {
    label: string;
    value: React.ReactNode;
    mono?: boolean;
  }) => (
    <div style={{ display: "flex", gap: 12, padding: "7px 0" }}>
      <div
        style={{
          width: 120,
          flexShrink: 0,
          fontSize: 12,
          color: T.ink3,
          fontWeight: 600,
        }}
      >
        {label}
      </div>
      <div
        style={{
          flex: 1,
          fontSize: 13,
          color: T.ink,
          fontFamily: mono ? T.mono : "inherit",
          whiteSpace: "pre-wrap",
        }}
      >
        {value}
      </div>
    </div>
  );

  return (
    <div
      onClick={onClose}
      style={{
        ...S.backdrop,
        zIndex: 100,
        fontFamily: T.font,
        padding: 20,
      }}
    >
      <div
        onClick={(e) => e.stopPropagation()}
        className="t-scale-in"
        style={{
          ...S.modal,
          width: 620,
          maxHeight: "94vh",
          overflow: "auto",
          color: T.ink,
        }}
      >
        <div
          style={{
            padding: "20px 26px 16px",
            borderBottom: `1px solid ${T.line}`,
            background: T.surfaceAlt,
            // 与 S.modal 圆角 20 对齐顶角
            borderRadius: "20px 20px 0 0",
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
            <div
              style={{
                fontSize: 11,
                color: T.ink3,
                letterSpacing: 2,
                fontWeight: 700,
              }}
            >
              外出申請 &gt; 詳細
            </div>
            <div style={{ flex: 1 }} />
            <span
              style={{
                ...S.pill,
                fontSize: 11,
                fontWeight: 700,
                padding: "2px 10px",
                background: sm[2],
                color: sm[1],
                border: `1px solid ${sm[3]}`,
              }}
            >
              {sm[0]}
            </span>
          </div>
          <div
            style={{
              fontSize: 20,
              fontWeight: 700,
              marginTop: 8,
              letterSpacing: -0.3,
            }}
          >
            {outing.student
              ? `${outing.student.name} さんの外出申請`
              : "外出申請"}
          </div>
          {outing.student && (
            <div
              style={{
                fontSize: 12,
                color: T.ink3,
                fontFamily: T.mono,
                marginTop: 2,
              }}
            >
              {outing.student.student_no} · {outing.student.room_no}
            </div>
          )}
        </div>

        <div style={{ padding: "16px 26px 4px" }}>
          <Field label="外出日" value={outing.outing_date} mono />
          <Field label="行き先" value={outing.destination || "（未記入）"} />
          <Field
            label="外出～帰寮"
            value={
              outing.leave_time || outing.return_time
                ? `${hhmm(outing.leave_time) || "—"} 〜 ${hhmm(outing.return_time) || "—"}`
                : "（未記入）"
            }
            mono
          />
          {/* 出租车预约没填就整行不显示 */}
          {outing.taxi_reservation_time && (
            <Field
              label="タクシー予約"
              value={hhmm(outing.taxi_reservation_time)}
              mono
            />
          )}
          <Field label="事由" value={outing.reason || "（未記入）"} />
          <Field
            label="提出時刻"
            value={formatDateTime(outing.submitted_at)}
            mono
          />
          {/* 处理老师那一行 —— 后端确认和却下共用同一组字段，所以标签按 status 分支：
              却下的显示「却下した先生」、确认的显示「確認した先生」 */}
          {outing.confirmed_by_name && (
            <Field
              label={
                outing.status === "rejected" ? "却下した先生" : "確認した先生"
              }
              value={`${outing.confirmed_by_name} 先生 · ${formatDateTime(
                outing.confirmed_at,
              )}`}
            />
          )}
          {outing.status === "rejected" && (
            <Field
              label="却下理由"
              value={outing.reject_reason || "（記入なし）"}
            />
          )}
          {outing.status === "withdrawn" && (
            <Field
              label="取消時刻"
              value={formatDateTime(outing.withdrawn_at)}
              mono
            />
          )}
        </div>

        <div
          style={{
            padding: "12px 26px 22px",
            borderTop: `1px solid ${T.line}`,
            marginTop: 12,
          }}
        >
          {isPending ? (
            <>
              <div
                style={{
                  fontSize: 11.5,
                  color: T.ink3,
                  marginBottom: 6,
                  fontWeight: 600,
                }}
              >
                却下理由（任意・却下する場合のみ寮生へ通知されます）
              </div>
              <textarea
                value={rejectReason}
                onChange={(e) => onChangeRejectReason(e.target.value)}
                rows={2}
                maxLength={500}
                placeholder="例：行き先が確認できないため"
                className="t-input"
                style={{
                  ...S.input,
                  width: "100%",
                  boxSizing: "border-box",
                  padding: "8px 12px",
                  border: `1px solid ${T.lineStrong}`,
                  resize: "vertical",
                }}
              />
              <div
                style={{
                  display: "flex",
                  gap: 10,
                  marginTop: 14,
                  alignItems: "center",
                }}
              >
                <button
                  onClick={onConfirm}
                  disabled={busy}
                  className="t-btn"
                  style={{
                    ...S.btnPrimary,
                    padding: "10px 22px",
                    cursor: busy ? "not-allowed" : "pointer",
                    opacity: busy ? 0.6 : 1,
                  }}
                >
                  {busy ? "処理中…" : "確認"}
                </button>
                <button
                  onClick={onReject}
                  disabled={busy}
                  className="t-btn"
                  style={{
                    ...S.btnDanger,
                    padding: "10px 22px",
                    cursor: busy ? "not-allowed" : "pointer",
                    opacity: busy ? 0.6 : 1,
                  }}
                >
                  却下
                </button>
                <button
                  onClick={onClose}
                  className="t-btn"
                  style={{
                    ...S.btnGhost,
                    marginLeft: "auto",
                    padding: "10px 18px",
                    fontSize: 12,
                    color: T.ink2,
                  }}
                >
                  閉じる
                </button>
              </div>
            </>
          ) : (
            <div style={{ display: "flex", alignItems: "center" }}>
              {/* 取消済＝学生自己按了「取りやめる」，老师根本没经手，写「処理済み」会让老师
                  以为是自己或同事处理过的 */}
              <div style={{ fontSize: 12, color: T.ink3 }}>
                {outing.status === "withdrawn"
                  ? "この外出は寮生本人が取りやめました"
                  : "この申請は既に処理済みです"}
              </div>
              <button
                onClick={onClose}
                className="t-btn"
                style={{
                  ...S.btnGhost,
                  marginLeft: "auto",
                  padding: "10px 18px",
                  fontSize: 12,
                  color: T.ink2,
                }}
              >
                閉じる
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
