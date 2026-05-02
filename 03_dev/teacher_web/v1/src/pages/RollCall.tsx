/**
 * 点呼ページ (#16-#20)
 * - 今日のセッション一覧
 * - セッション開始/終了
 * - 座席ボード (ポーリング)
 */
import { useEffect, useRef, useState } from "react";
import { api, type RollCallSessionOut, type RollCallBoardOut } from "../api/client";
import { useAuth } from "../store/auth";
import clsx from "clsx";

const STATUS_LABEL: Record<string, string> = {
  init: "未",
  present: "出席",
  late: "遅刻",
  absent: "欠席",
  exempt_range: "外出中",
};

const STATUS_COLOR: Record<string, string> = {
  init: "bg-gray-100 text-gray-500",
  present: "bg-green-100 text-green-700",
  late: "bg-amber-100 text-amber-700",
  absent: "bg-red-100 text-red-700",
  exempt_range: "bg-blue-100 text-blue-700",
};

export default function RollCallPage() {
  const { token } = useAuth();
  const [sessions, setSessions] = useState<RollCallSessionOut[]>([]);
  const [activeSession, setActiveSession] = useState<RollCallSessionOut | null>(null);
  const [board, setBoard] = useState<RollCallBoardOut | null>(null);
  const [loading, setLoading] = useState(true);
  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null);

  async function loadSessions() {
    setLoading(true);
    try {
      const data = await api.rollcallTodaySessions(token!);
      setSessions(data);
    } finally {
      setLoading(false);
    }
  }

  async function loadBoard(session_id: string) {
    try {
      const data = await api.rollcallBoard(session_id, token!);
      setBoard(data);
    } catch { /* ignore */ }
  }

  useEffect(() => { loadSessions(); }, []);

  // ポーリング: running 中のセッションは 5 秒ごとボード更新
  useEffect(() => {
    if (pollRef.current) clearInterval(pollRef.current);
    if (activeSession?.session_status === "running") {
      pollRef.current = setInterval(() => loadBoard(activeSession.id), 5000);
    }
    return () => { if (pollRef.current) clearInterval(pollRef.current); };
  }, [activeSession?.id, activeSession?.session_status]);

  async function handleSelect(s: RollCallSessionOut) {
    setActiveSession(s);
    await loadBoard(s.id);
  }

  async function handleStart() {
    if (!activeSession) return;
    const updated = await api.rollcallStart(activeSession.id, token!);
    setActiveSession(updated);
    loadSessions();
    loadBoard(updated.id);
  }

  async function handleEnd() {
    if (!activeSession) return;
    if (!confirm("点呼を終了します。未チェックの学生は欠席になります。")) return;
    const updated = await api.rollcallEnd(activeSession.id, token!);
    setActiveSession(updated);
    loadSessions();
    loadBoard(updated.id);
  }

  const sessionLabel = (s: RollCallSessionOut) => {
    const dorm = s.dorm_unit_set.includes(4) ? "女寮" : "男寮";
    const type = s.session_type === "morning" ? "朝" : "晩";
    return `${dorm} ${type}点呼`;
  };

  const sessionStatusColor = (status: string) =>
    status === "running" ? "badge-approved" : status === "ended" ? "bg-gray-100 text-gray-500 inline-flex px-2 py-0.5 rounded-full text-xs font-medium" : "badge-pending";

  return (
    <div className="p-6 max-w-5xl mx-auto">
      <h1 className="text-xl font-bold mb-5">点呼</h1>

      <div className="flex gap-6">
        {/* セッション一覧 */}
        <div className="w-64 shrink-0">
          <h2 className="text-xs font-semibold text-gray-500 uppercase mb-2">今日のセッション</h2>
          {loading ? (
            <div className="text-gray-400 text-sm">読み込み中…</div>
          ) : sessions.length === 0 ? (
            <div className="card text-center py-6 text-gray-400 text-sm">
              セッションがありません
            </div>
          ) : (
            <div className="space-y-2">
              {sessions.map((s) => (
                <button
                  key={s.id}
                  onClick={() => handleSelect(s)}
                  className={clsx(
                    "w-full text-left card p-3 hover:shadow-md transition-all",
                    activeSession?.id === s.id && "ring-2 ring-brand-500"
                  )}
                >
                  <div className="font-medium text-sm">{sessionLabel(s)}</div>
                  <div className="flex items-center gap-2 mt-1">
                    <span className={sessionStatusColor(s.session_status)}>
                      {s.session_status === "running" ? "進行中" : s.session_status === "ended" ? "終了" : "待機"}
                    </span>
                  </div>
                  <div className="text-xs text-gray-400 mt-1">
                    {new Date(s.scheduled_window_start_at).toLocaleTimeString("ja-JP", { hour: "2-digit", minute: "2-digit" })}
                    {" "}〜{" "}
                    {new Date(s.scheduled_late_end_at).toLocaleTimeString("ja-JP", { hour: "2-digit", minute: "2-digit" })}
                  </div>
                </button>
              ))}
            </div>
          )}
        </div>

        {/* ボード */}
        <div className="flex-1">
          {!activeSession ? (
            <div className="card text-center py-16 text-gray-400">
              セッションを選択してください
            </div>
          ) : (
            <>
              {/* コントロールバー */}
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h2 className="text-lg font-bold">{sessionLabel(activeSession)}</h2>
                  {board && (
                    <p className="text-xs text-gray-500 mt-0.5">
                      出席 {board.summary.present ?? 0} / 遅刻 {board.summary.late ?? 0} / 欠席 {board.summary.absent ?? 0}
                    </p>
                  )}
                </div>
                <div className="flex gap-2">
                  {activeSession.session_status === "draft" && (
                    <button onClick={handleStart} className="btn-primary text-sm">
                      開始
                    </button>
                  )}
                  {activeSession.session_status === "running" && (
                    <button onClick={handleEnd} className="btn-danger text-sm">
                      終了
                    </button>
                  )}
                  <button
                    onClick={() => loadBoard(activeSession.id)}
                    className="btn-ghost text-xs"
                  >
                    更新
                  </button>
                </div>
              </div>

              {/* 座席グリッド */}
              {board ? (
                <div className="grid grid-cols-4 sm:grid-cols-5 md:grid-cols-6 gap-2">
                  {board.entries.map((e) => (
                    <div
                      key={e.student_id}
                      className={clsx(
                        "rounded-lg p-2 text-center text-xs",
                        STATUS_COLOR[e.base_status] ?? "bg-gray-100"
                      )}
                    >
                      <div className="font-semibold truncate">{e.name}</div>
                      <div className="text-gray-500 mt-0.5">{e.room_no}</div>
                      <div className="mt-1 font-bold">
                        {STATUS_LABEL[e.base_status] ?? e.base_status}
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="card text-center py-8 text-gray-400">
                  ボードを読み込んでいます…
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
}
