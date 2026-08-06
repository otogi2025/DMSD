import React from "react";
import { RYO, S } from "../theme";
import { api } from "../api/client";
import type {
  StudyTodayOut,
  StudyAbsenceRequestOut,
  StudyRosterItem,
  TeacherProfile,
} from "../api/types";
import { canManage, C_STUDY } from "../api/permissions";

// 源 index.html 14827-15786（study-attendance-page 块）。界面原样搬，仅作用域引用改写。
// Task #17 夜学習出席页 — §11.1 P0 + §7.3 + iOS StudyAPI 对齐 (5-27)
// 学習担当老师当天夜学習出席管理:
//   - studyTodayAttendees 拉当天对象学生 + 状态 (init/present/late/absent)
//   - absenceRequests 拉学生提交的请假一览 + 一键 ✅/❌
//   - studyCheckin 手动出席（NFC 失败时的人工补签）
//   - studyFinalize 学習結束 (没碰 NFC 的统一标 absent)
//   - cancelToday 「今日学習中止」开关 (学習担当權限)
// 对齐: backend study.py + iOS StudyAPI.swift (3 次 NFC 出席) + spec §7.3.10
export function StudyAttendancePage({
  teacher,
  authToken,
}: {
  teacher: TeacherProfile | null;
  authToken: string | null;
}) {
  const T = RYO;
  // 权限：C_STUDY 簇里「一般宿管」「申請承認専用」两组只有 VIEW，后端 routers/study.py 的
  // 手动出席/结束确定/当日中止/欠席承认/名簿增删全 require_permission(C_STUDY, MANAGE)。
  // 无 MANAGE 时隐藏全部写按钮，避免点了必被 403（与 AccountsPage/InfoPage 同款门控）。
  const canWrite = !!teacher && canManage(teacher, C_STUDY);
  const [view, setView] = React.useState("attendance"); // attendance / absence-inbox / roster
  const [today, setToday] = React.useState<StudyTodayOut | null>(null); // studyTodayAttendees 返
  const [absenceList, setAbsenceList] = React.useState<
    StudyAbsenceRequestOut[] | null
  >(null);
  const [loading, setLoading] = React.useState(false);
  const [err, setErr] = React.useState("");
  const [acting, setActing] = React.useState<Record<string, boolean>>({}); // student_id → boolean 动作中
  // 学習対象名簿 管理（杭田 060604 五-2）
  const [roster, setRoster] = React.useState<StudyRosterItem[] | null>(null); // studyRoster 返回的在籍者一览
  const [rosterErr, setRosterErr] = React.useState("");
  const [addNo, setAddNo] = React.useState(""); // 「学生追加」输入框里的学号

  const refetch = React.useCallback(
    async (opts?: { silent?: boolean }) => {
      if (!authToken) return;
      if (!opts?.silent) setLoading(true);
      setErr("");
      try {
        const todayData = await api.studyTodayAttendees(authToken);
        setToday(todayData);
        // 欠席届两路拉取（审查 web#6）：status=pending 全量（只拉今天会漏
        // 「今天提交、対象日=明天」的待审）+ 対象日=今天含已决（当日上下文）。
        // 「今天」用后端 target_date 的 JST 口径，不用浏览器本地时区。
        // allSettled 各自容错——一路失败不拖垮另一路（web#121 同构教训）
        const [pendRes, todaysRes] = await Promise.allSettled([
          api.absenceRequests(authToken, undefined, "pending"),
          api.absenceRequests(authToken, todayData.target_date),
        ]);
        const merged: StudyAbsenceRequestOut[] = [];
        const seen = new Set<string>();
        for (const res of [pendRes, todaysRes]) {
          if (res.status !== "fulfilled") continue;
          for (const a of res.value || []) {
            if (seen.has(a.id)) continue;
            seen.add(a.id);
            merged.push(a);
          }
        }
        if (pendRes.status === "rejected" && todaysRes.status === "rejected") {
          throw pendRes.reason;
        }
        merged.sort((x, y) => x.submitted_at.localeCompare(y.submitted_at));
        setAbsenceList(merged);
      } catch (e) {
        if (opts?.silent) return; // 静默自动刷新失败时不弹错误盖住界面，下次轮询再试
        const ex = e as { status?: number };
        if (ex && ex.status === 403) {
          setErr("このページは「夜学習担当」権限が必要です");
        } else if (ex && ex.status) {
          setErr(`サーバーエラー (${ex.status})`);
        } else {
          setErr(
            "サーバーに接続できません。しばらくしてから再度お試しください",
          );
        }
      } finally {
        if (!opts?.silent) setLoading(false);
      }
    },
    [authToken],
  );

  React.useEffect(() => {
    refetch();
  }, [refetch]);

  // 自动刷新：在「出席リスト」视图下每 15 秒静默拉一次后端，老师不用手动点「再読み込み」就是最新。
  // ※ 学生刷卡瞬间座位变绿那种「真·实时反映」依赖晚自习 NFC 受付的后端实装 + WebSocket 推送
  //   （跟点呼同一套机制），那块后端还没写，留 v1.1 实装。
  React.useEffect(() => {
    if (!authToken || view !== "attendance") return;
    const id = setInterval(() => refetch({ silent: true }), 15000);
    return () => clearInterval(id);
  }, [authToken, view, refetch]);

  const doManualCheckin = async (student_id: string) => {
    if (acting[student_id]) return;
    setActing((m) => ({ ...m, [student_id]: true }));
    try {
      await api.studyCheckin(student_id, authToken!);
      await refetch();
    } catch (e) {
      const ex = e as { status?: number };
      console.warn("[StudyAttendance] checkin 失敗", e);
      setErr(`出席登録に失敗 (${(ex && ex.status) || "network"})`);
    } finally {
      setActing((m) => ({ ...m, [student_id]: false }));
    }
  };

  const doFinalize = async () => {
    if (acting.__finalize) return; // TW-102：防慢网下二次点击重复 finalize
    if (
      !window.confirm(
        "夜学習を終了し、未チェックイン寮生を欠席扱いにします。よろしいですか?",
      )
    )
      return;
    setActing((m) => ({ ...m, __finalize: true }));
    try {
      await api.studyFinalize(authToken!);
      await refetch();
    } catch (e) {
      const ex = e as { status?: number };
      setErr(`夜学習終了に失敗 (${(ex && ex.status) || "network"})`);
    } finally {
      setActing((m) => ({ ...m, __finalize: false }));
    }
  };

  const doCancelToday = async () => {
    if (acting.__cancel) return; // TW-102：防慢网下二次点击重复中止
    if (
      // TW-036：去掉「学生にもプッシュ通知が送信されます」—— 后端 cancel-today 只把未出席
      // 学生置 exempt + 撤缺席扣分，不发任何推送 / 通知。原文案让老师误以为已通知学生今晚停学，
      // 实际学生零通知。推送实装(v1.1)后再恢复该承诺。
      !window.confirm("今日の夜学習を中止します。よろしいですか?")
    )
      return;
    setActing((m) => ({ ...m, __cancel: true }));
    try {
      await api.cancelToday(authToken!);
      await refetch();
    } catch (e) {
      const ex = e as { status?: number };
      setErr(`夜学習中止に失敗 (${(ex && ex.status) || "network"})`);
    } finally {
      setActing((m) => ({ ...m, __cancel: false }));
    }
  };

  const doDecideAbsence = async (
    id: string,
    decision: "approved" | "rejected",
  ) => {
    if (acting[id]) return; // 与 doFinalize / doCancelToday 一致：防双击窗口重复批准/驳回
    setActing((m) => ({ ...m, [id]: true }));
    try {
      await api.decideAbsence(id, decision, undefined, authToken!);
      await refetch();
    } catch (e) {
      const ex = e as { status?: number };
      setErr(`欠席届処理に失敗 (${(ex && ex.status) || "network"})`);
    } finally {
      setActing((m) => ({ ...m, [id]: false }));
    }
  };

  // 名簿一览：进「名簿管理」tab 时拉一次（与出席 / 欠席不同接口，单独 fetch）
  const refetchRoster = React.useCallback(async () => {
    if (!authToken) return;
    setRosterErr("");
    try {
      const list = await api.studyRoster(authToken);
      setRoster(list || []);
    } catch (e) {
      const ex = e as { status?: number };
      if (ex && ex.status === 403) {
        setRosterErr("名簿管理は「夜学習担当 / 寮務」権限が必要です");
      } else {
        setRosterErr(`名簿の取得に失敗 (${(ex && ex.status) || "network"})`);
      }
    }
  }, [authToken]);

  React.useEffect(() => {
    if (view === "roster") refetchRoster();
  }, [view, refetchRoster]);

  // 学生追加：输入框填学号 → POST /study/roster { student_no }
  const doAddToRoster = async () => {
    const no = (addNo || "").trim();
    if (!/^\d{6}$/.test(no)) {
      setRosterErr("学籍番号は6桁（学年2＋クラス2＋番号2）で入力してください");
      return;
    }
    setRosterErr("");
    try {
      await api.studyRosterAdd({ student_no: no }, authToken!);
      setAddNo("");
      await refetchRoster();
    } catch (e) {
      const ex = e as { status?: number };
      if (ex && ex.status === 404) {
        setRosterErr(`学籍番号 ${no} の寮生が見つかりません`);
      } else if (ex && ex.status === 409) {
        setRosterErr(`学籍番号 ${no} は既に名簿に登録済みです`);
      } else {
        setRosterErr(`追加に失敗 (${(ex && ex.status) || "network"})`);
      }
    }
  };

  // 从学習对象名簿移出：DELETE /study/roster/{student_id}（软删）
  const doRemoveFromRoster = async (student_id: string, name: string) => {
    if (!window.confirm(`${name} さんを夜学習対象名簿から外しますか?`)) return;
    setActing((m) => ({ ...m, [student_id]: true }));
    try {
      await api.studyRosterRemove(student_id, authToken!);
      await refetchRoster();
    } catch (e) {
      const ex = e as { status?: number };
      setRosterErr(`名簿から外すのに失敗 (${(ex && ex.status) || "network"})`);
    } finally {
      setActing((m) => ({ ...m, [student_id]: false }));
    }
  };

  const statusBadge = (
    s: { status: string } | null,
  ): [string, string, string, string] => {
    if (!s) return ["未出席", T.ink3, T.graySoft, T.grayBorder];
    if (s.status === "present" || s.status === "ok")
      return ["出席", T.ok, T.okSoft, T.okBorder];
    if (s.status === "late") return ["遅刻", T.late, T.lateSoft, T.lateBorder];
    if (s.status === "absent")
      return ["欠席", T.danger, T.dangerSoft, T.dangerBorder];
    // cancel-today 后 checkin.status 可为 exempt（予定列对应「中止・免除」）
    if (s.status === "exempt")
      return ["免除", T.ink2, T.graySoft, T.grayBorder];
    return ["—", T.ink3, T.graySoft, T.grayBorder];
  };

  const expectedBadge = (
    e: string,
  ): [string, string, string, string] | null => {
    if (e === "exempted_outstay")
      return ["外泊免除", T.ink2, T.graySoft, T.grayBorder];
    if (e === "exempted_online")
      return ["オンライン学習", T.cobaltDeep, T.cobaltSoft, T.infoBorder];
    if (e === "exempted_absence")
      return ["欠席承認済", T.cobaltDeep, T.cobaltSoft, T.infoBorder];
    if (e === "exempted_cancel")
      return ["中止・免除", T.ink2, T.graySoft, T.grayBorder];
    return null;
  };

  if (loading && !today) {
    return (
      <div style={{ padding: 48, textAlign: "center", color: T.ink3 }}>
        読み込み中…
      </div>
    );
  }

  if (err && !today) {
    return (
      <div style={{ padding: "28px 32px 48px" }}>
        <h1
          style={{
            fontSize: 24,
            fontWeight: 700,
            margin: "4px 0 18px",
          }}
        >
          夜学習出席
        </h1>
        <div
          style={{
            padding: 18,
            background: T.dangerSoft,
            color: T.danger,
            border: `1px solid ${T.dangerBorder}`,
            borderRadius: 12,
            fontSize: 13,
          }}
        >
          {err}
        </div>
      </div>
    );
  }

  const summary = (today && today.summary) || {
    expected: 0,
    checked_in: 0,
    late: 0,
    absent: 0,
  };
  const attendees = (today && today.expected_attendees) || [];
  const pendingAbsence = (absenceList || []).filter(
    (a) => a.status === "pending",
  );

  return (
    <div style={{ padding: "28px 32px 48px" }}>
      <div
        style={{
          display: "flex",
          alignItems: "baseline",
          justifyContent: "space-between",
          marginBottom: 18,
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
            {/* 7-17 适老化拍板⑤：眉头首段与左栏用词统一 — 原「夜学習担当」跟左栏「夜学習出席」对不上 */}
            夜学習出席 &gt;{" "}
            {view === "attendance"
              ? "出席"
              : view === "absence-inbox"
                ? "欠席届"
                : "名簿管理"}
          </div>
          <h1
            style={{
              fontSize: 24,
              fontWeight: 700,
              margin: "4px 0 0",
              letterSpacing: -0.3,
            }}
          >
            夜学習出席 {today && `· ${today.target_date}`}
          </h1>
        </div>
        <div style={{ display: "flex", gap: 8 }}>
          <button
            onClick={() => setView("attendance")}
            className="t-btn"
            style={{
              padding: "8px 14px",
              background: view === "attendance" ? T.cobalt : T.surface,
              color: view === "attendance" ? "#fff" : T.ink2,
              border: `1px solid ${view === "attendance" ? T.cobalt : T.lineStrong}`,
              borderRadius: 10,
              fontFamily: "inherit",
              fontSize: 12,
              fontWeight: 700,
              cursor: "pointer",
              transition: T.ease,
            }}
          >
            出席リスト
          </button>
          <button
            onClick={() => setView("absence-inbox")}
            className="t-btn"
            style={{
              padding: "8px 14px",
              background: view === "absence-inbox" ? T.cobalt : T.surface,
              color: view === "absence-inbox" ? "#fff" : T.ink2,
              border: `1px solid ${view === "absence-inbox" ? T.cobalt : T.lineStrong}`,
              borderRadius: 10,
              fontFamily: "inherit",
              fontSize: 12,
              fontWeight: 700,
              cursor: "pointer",
              transition: T.ease,
            }}
          >
            欠席届 {pendingAbsence.length > 0 && `(${pendingAbsence.length})`}
          </button>
          <button
            onClick={() => setView("roster")}
            className="t-btn"
            style={{
              padding: "8px 14px",
              background: view === "roster" ? T.cobalt : T.surface,
              color: view === "roster" ? "#fff" : T.ink2,
              border: `1px solid ${view === "roster" ? T.cobalt : T.lineStrong}`,
              borderRadius: 10,
              fontFamily: "inherit",
              fontSize: 12,
              fontWeight: 700,
              cursor: "pointer",
              transition: T.ease,
            }}
          >
            名簿管理
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
            borderRadius: 10,
            fontSize: 12,
            marginBottom: 14,
          }}
        >
          {err}
        </div>
      )}

      {view === "attendance" && (
        <>
          <div
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(4, 1fr)",
              gap: 12,
              marginBottom: 18,
            }}
          >
            {(
              [
                ["予定", summary.expected, T.cobalt],
                ["出席", summary.checked_in, T.ok],
                ["遅刻", summary.late, T.late],
                ["欠席", summary.absent, T.danger],
              ] as [string, number, string][]
            ).map(([l, v, c]) => (
              <div
                key={l}
                style={{
                  ...S.card,
                  padding: "14px 18px",
                }}
              >
                <div
                  style={{
                    fontSize: 11,
                    color: T.ink3,
                    letterSpacing: 1,
                    fontWeight: 600,
                    marginBottom: 4,
                  }}
                >
                  {l}
                </div>
                <div
                  style={{
                    fontSize: 28,
                    fontWeight: 700,
                    color: c,
                    fontFamily: T.mono,
                  }}
                >
                  {v}
                </div>
              </div>
            ))}
          </div>

          <div style={{ display: "flex", gap: 10, marginBottom: 14 }}>
            {canWrite && (
              <button
                onClick={doFinalize}
                disabled={!!acting.__finalize}
                className="t-btn"
                style={{
                  ...S.btnPrimary,
                  padding: "10px 18px",
                  cursor: acting.__finalize ? "not-allowed" : "pointer",
                  opacity: acting.__finalize ? 0.6 : 1,
                }}
              >
                夜学習終了（未出席を欠席に確定）
              </button>
            )}
            {canWrite && (
              <button
                onClick={doCancelToday}
                disabled={!!acting.__cancel}
                className="t-btn"
                style={{
                  ...S.btnGhost,
                  padding: "10px 18px",
                  color: T.warn,
                  border: `1px solid ${T.warnBorder}`,
                  cursor: acting.__cancel ? "not-allowed" : "pointer",
                  opacity: acting.__cancel ? 0.6 : 1,
                }}
              >
                今日の夜学習を中止
              </button>
            )}
            <button
              onClick={() => refetch()}
              className="t-btn"
              style={{
                ...S.btnGhost,
                marginLeft: "auto",
                padding: "10px 14px",
                fontSize: 12,
                fontWeight: 400,
                color: T.ink2,
              }}
            >
              再読み込み
            </button>
          </div>

          <div
            style={{
              ...S.card,
              overflow: "hidden",
            }}
          >
            <div
              style={{
                display: "grid",
                gridTemplateColumns: "80px 100px 1fr 120px 130px 110px",
                background: T.surfaceAlt,
                color: T.ink3,
                fontSize: 11,
                fontWeight: 600,
                letterSpacing: 1,
                borderBottom: `1px solid ${T.line}`,
              }}
            >
              {["部屋", "学籍番号", "氏名", "予定", "状態", "操作"].map((h) => (
                <div key={h} style={{ padding: "10px 14px" }}>
                  {h}
                </div>
              ))}
            </div>
            {/* 7-17 适老化拍板⑥：空状态不只报「没有」，还要指出下一步去哪 */}
            {attendees.length === 0 && (
              <div
                style={{
                  padding: 40,
                  textAlign: "center",
                  color: T.ink3,
                  fontSize: 13,
                }}
              >
                <div>対象寮生がいません</div>
                <div style={{ marginTop: 8, fontSize: 12 }}>
                  名簿管理から対象寮生を登録してください
                </div>
                <button
                  onClick={() => setView("roster")}
                  className="t-btn"
                  style={{
                    marginTop: 12,
                    padding: "8px 16px",
                    background: T.cobaltSoft,
                    color: T.cobaltDeep,
                    border: "none",
                    borderRadius: 10,
                    fontFamily: "inherit",
                    fontSize: 12,
                    fontWeight: 600,
                    cursor: "pointer",
                    transition: T.ease,
                  }}
                >
                  名簿管理へ →
                </button>
              </div>
            )}
            {attendees.map((a, i) => {
              const sb = statusBadge(a.checkin);
              const eb = expectedBadge(a.expected_status);
              const canCheckin =
                a.expected_status === "expected" &&
                (!a.checkin || !["present", "ok"].includes(a.checkin.status));
              return (
                <div
                  key={a.student_id}
                  className="t-row"
                  style={{
                    display: "grid",
                    gridTemplateColumns: "80px 100px 1fr 120px 130px 110px",
                    borderTop: i > 0 ? `1px solid ${T.line}` : "none",
                    alignItems: "center",
                    fontSize: 13,
                  }}
                >
                  <div style={{ padding: "10px 14px", fontFamily: T.mono }}>
                    {a.room_no}
                  </div>
                  <div
                    style={{
                      padding: "10px 14px",
                      fontFamily: T.mono,
                      color: T.ink2,
                    }}
                  >
                    {a.student_no}
                  </div>
                  <div style={{ padding: "10px 14px", fontWeight: 600 }}>
                    {a.name}
                  </div>
                  <div style={{ padding: "10px 14px" }}>
                    {eb ? (
                      <span
                        style={{
                          ...S.pill,
                          fontSize: 11,
                          fontWeight: 700,
                          padding: "2px 8px",
                          borderRadius: 4,
                          background: eb[2],
                          color: eb[1],
                          border: `1px solid ${eb[3]}`,
                        }}
                      >
                        {eb[0]}
                      </span>
                    ) : (
                      <span
                        style={{
                          fontSize: 11,
                          color: T.ink3,
                        }}
                      >
                        予定
                      </span>
                    )}
                  </div>
                  <div style={{ padding: "10px 14px" }}>
                    <span
                      style={{
                        ...S.pill,
                        fontSize: 11,
                        fontWeight: 700,
                        padding: "2px 8px",
                        borderRadius: 4,
                        background: sb[2],
                        color: sb[1],
                        border: `1px solid ${sb[3]}`,
                      }}
                    >
                      {sb[0]}
                    </span>
                    {a.checkin && a.checkin.checked_at && (
                      <span
                        style={{
                          marginLeft: 6,
                          fontSize: 10,
                          fontFamily: T.mono,
                          color: T.ink3,
                        }}
                      >
                        {new Date(a.checkin.checked_at).toLocaleTimeString(
                          "ja-JP",
                          {
                            hour: "2-digit",
                            minute: "2-digit",
                          },
                        )}
                      </span>
                    )}
                  </div>
                  <div style={{ padding: "10px 14px" }}>
                    {canWrite && canCheckin && (
                      <button
                        onClick={() => doManualCheckin(a.student_id)}
                        disabled={acting[a.student_id]}
                        className="t-btn"
                        style={{
                          ...S.btnSmall,
                          padding: "4px 10px",
                          background: T.cobalt,
                          color: "#fff",
                          border: "none",
                          fontSize: 11,
                          cursor: acting[a.student_id]
                            ? "not-allowed"
                            : "pointer",
                        }}
                      >
                        {acting[a.student_id] ? "..." : "出席にする"}
                      </button>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </>
      )}

      {view === "absence-inbox" && (
        <div
          style={{
            ...S.card,
            overflow: "hidden",
          }}
        >
          <div
            style={{
              display: "grid",
              gridTemplateColumns: "170px 100px 64px 1fr 90px 140px 170px",
              background: T.surfaceAlt,
              color: T.ink3,
              fontSize: 11,
              fontWeight: 600,
              letterSpacing: 1,
              borderBottom: `1px solid ${T.line}`,
            }}
          >
            {["寮生", "対象日", "期間", "理由", "状態", "提出時刻", "操作"].map(
              (h) => (
                <div key={h} style={{ padding: "10px 14px" }}>
                  {h}
                </div>
              ),
            )}
          </div>
          {(absenceList || []).length === 0 && (
            <div
              style={{
                padding: 40,
                textAlign: "center",
                color: T.ink3,
                fontSize: 13,
              }}
            >
              欠席届がありません
            </div>
          )}
          {(absenceList || []).map((a, i) => (
            <div
              key={a.id}
              className="t-row"
              style={{
                display: "grid",
                gridTemplateColumns: "170px 100px 64px 1fr 90px 140px 170px",
                borderTop: i > 0 ? `1px solid ${T.line}` : "none",
                alignItems: "center",
                fontSize: 13,
              }}
            >
              {/* 学生 / 対象日 / 期間 — 原来这三列都没有，老师看不到「谁请
                  哪天哪一段的假」就能点承認/却下（审查 web#6 误批风险） */}
              <div style={{ padding: "10px 14px" }}>
                {a.student_name ? (
                  <>
                    <div style={{ fontWeight: 600 }}>{a.student_name}</div>
                    {a.student_no && (
                      <div
                        style={{
                          fontSize: 11,
                          color: T.ink3,
                          fontFamily: T.mono,
                        }}
                      >
                        {a.student_no}
                        {a.room_no ? ` · ${a.room_no}` : ""}
                      </div>
                    )}
                  </>
                ) : (
                  <span style={{ fontFamily: T.mono, fontSize: 11 }}>
                    {String(a.student_id).slice(0, 8)}…
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
                {a.target_date}
              </div>
              <div style={{ padding: "10px 14px", fontSize: 12 }}>
                {a.period === "first_half"
                  ? "前半"
                  : a.period === "second_half"
                    ? "後半"
                    : "全日"}
              </div>
              <div style={{ padding: "10px 14px" }}>{a.reason}</div>
              <div style={{ padding: "10px 14px" }}>
                <span
                  style={{
                    ...S.pill,
                    fontSize: 11,
                    fontWeight: 700,
                    padding: "2px 8px",
                    borderRadius: 4,
                    background:
                      a.status === "pending"
                        ? T.warnSoft
                        : a.status === "approved"
                          ? T.okSoft
                          : T.dangerSoft,
                    color:
                      a.status === "pending"
                        ? T.warn
                        : a.status === "approved"
                          ? T.ok
                          : T.danger,
                    border: `1px solid ${
                      a.status === "pending"
                        ? T.warnBorder
                        : a.status === "approved"
                          ? T.okBorder
                          : T.dangerBorder
                    }`,
                  }}
                >
                  {a.status === "pending"
                    ? "審査待ち"
                    : a.status === "approved"
                      ? "承認"
                      : "却下"}
                </span>
              </div>
              <div
                style={{
                  padding: "10px 14px",
                  fontFamily: T.mono,
                  fontSize: 11,
                  color: T.ink3,
                }}
              >
                {new Date(a.submitted_at).toLocaleString("ja-JP", {
                  timeZone: "Asia/Tokyo",
                })}
              </div>
              <div style={{ padding: "10px 14px", display: "flex", gap: 6 }}>
                {canWrite && a.status === "pending" && (
                  <>
                    <button
                      onClick={() => doDecideAbsence(a.id, "approved")}
                      disabled={acting[a.id]}
                      className="t-btn"
                      style={{
                        ...S.btnSmall,
                        padding: "4px 12px",
                        background: T.ok,
                        color: "#fff",
                        border: "none",
                        fontSize: 11,
                        fontWeight: 700,
                        cursor: acting[a.id] ? "not-allowed" : "pointer",
                      }}
                    >
                      承認
                    </button>
                    <button
                      onClick={() => doDecideAbsence(a.id, "rejected")}
                      disabled={acting[a.id]}
                      className="t-btn"
                      style={{
                        ...S.btnSmall,
                        padding: "4px 12px",
                        color: T.danger,
                        border: `1px solid ${T.dangerBorder}`,
                        fontSize: 11,
                        fontWeight: 700,
                        cursor: acting[a.id] ? "not-allowed" : "pointer",
                      }}
                    >
                      却下
                    </button>
                  </>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {view === "roster" && (
        <>
          {rosterErr && (
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
              {rosterErr}
            </div>
          )}

          {/* 学生追加：输学号 → 加入名簿 */}
          <div
            style={{
              display: "flex",
              gap: 10,
              alignItems: "center",
              marginBottom: 14,
              ...S.card,
              padding: "14px 18px",
            }}
          >
            {canWrite && (
              <>
                <label style={{ fontSize: 12, color: T.ink2, fontWeight: 600 }}>
                  学籍番号で追加
                </label>
                <input
                  type="text"
                  inputMode="numeric"
                  maxLength={6}
                  placeholder="例：060218"
                  value={addNo}
                  onChange={(e) =>
                    setAddNo(e.target.value.replace(/[^\d]/g, ""))
                  }
                  onKeyDown={(e) => {
                    if (e.key === "Enter") doAddToRoster();
                  }}
                  className="t-input"
                  style={{
                    ...S.input,
                    width: 140,
                    padding: "8px 12px",
                    border: `1px solid ${T.lineStrong}`,
                    fontFamily: T.mono,
                  }}
                />
                <button
                  onClick={doAddToRoster}
                  className="t-btn"
                  style={{
                    ...S.btnPrimary,
                    padding: "8px 16px",
                    fontSize: 12,
                  }}
                >
                  寮生追加
                </button>
              </>
            )}
            <button
              onClick={refetchRoster}
              className="t-btn"
              style={{
                ...S.btnGhost,
                marginLeft: "auto",
                padding: "8px 14px",
                fontSize: 12,
                fontWeight: 400,
                color: T.ink2,
              }}
            >
              再読み込み
            </button>
          </div>

          {/* 名簿在籍者一览 */}
          <div
            style={{
              ...S.card,
              overflow: "hidden",
            }}
          >
            <div
              style={{
                display: "grid",
                gridTemplateColumns: "110px 1fr 120px 90px 130px",
                background: T.surfaceAlt,
                color: T.ink3,
                fontSize: 11,
                fontWeight: 600,
                letterSpacing: 1,
                borderBottom: `1px solid ${T.line}`,
              }}
            >
              {["学籍番号", "氏名", "部屋", "寮", "操作"].map((h) => (
                <div key={h} style={{ padding: "10px 14px" }}>
                  {h}
                </div>
              ))}
            </div>
            {roster === null && (
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
            {roster !== null && roster.length === 0 && (
              <div
                style={{
                  padding: 40,
                  textAlign: "center",
                  color: T.ink3,
                  fontSize: 13,
                }}
              >
                名簿に登録された寮生がいません
              </div>
            )}
            {(roster || []).map((r, i) => (
              <div
                key={r.student_id}
                className="t-row"
                style={{
                  display: "grid",
                  gridTemplateColumns: "110px 1fr 120px 90px 130px",
                  borderTop: i > 0 ? `1px solid ${T.line}` : "none",
                  alignItems: "center",
                  fontSize: 13,
                }}
              >
                <div
                  style={{
                    padding: "10px 14px",
                    fontFamily: T.mono,
                    color: T.ink2,
                  }}
                >
                  {r.student_no}
                </div>
                <div style={{ padding: "10px 14px" }}>{r.name}</div>
                <div
                  style={{
                    padding: "10px 14px",
                    fontFamily: T.mono,
                    color: T.ink3,
                  }}
                >
                  {r.room_no}
                </div>
                <div style={{ padding: "10px 14px", color: T.ink3 }}>
                  {r.dorm_unit}
                </div>
                <div style={{ padding: "10px 14px" }}>
                  {canWrite && (
                    <button
                      onClick={() => doRemoveFromRoster(r.student_id, r.name)}
                      disabled={acting[r.student_id]}
                      className="t-btn"
                      style={{
                        ...S.btnSmall,
                        padding: "4px 12px",
                        color: T.danger,
                        border: `1px solid ${T.dangerBorder}`,
                        fontSize: 11,
                        fontWeight: 700,
                        cursor: acting[r.student_id]
                          ? "not-allowed"
                          : "pointer",
                      }}
                    >
                      名簿から外す
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  );
}
