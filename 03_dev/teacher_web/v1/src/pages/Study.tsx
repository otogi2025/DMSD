/**
 * 学習ダッシュボード (#14-#15 #20)
 * - 今日の出席者一覧 (リアルタイム風)
 * - 欠席届 inbox + 承認/拒否
 * - 今日学習中止スイッチ (学習担当のみ)
 */
import { useEffect, useState } from "react";
import { api, type StudyTodayOut, type StudyAbsenceRequestOut } from "../api/client";
import { useAuth } from "../store/auth";
import clsx from "clsx";

type Tab = "attendance" | "absences";

function statusColor(status: string) {
  const map: Record<string, string> = {
    present: "text-green-600 font-semibold",
    late: "text-amber-600 font-semibold",
    absent: "text-red-600 font-semibold",
    init: "text-gray-400",
    exempt: "text-gray-400 italic",
  };
  const label: Record<string, string> = {
    present: "出席",
    late: "遅刻",
    absent: "欠席",
    init: "未",
    exempt: "免除",
  };
  return { cls: map[status] ?? "text-gray-600", label: label[status] ?? status };
}

export default function StudyPage() {
  const { token, teacher } = useAuth();
  const [tab, setTab] = useState<Tab>("attendance");
  const [today, setToday] = useState<StudyTodayOut | null>(null);
  const [absences, setAbsences] = useState<StudyAbsenceRequestOut[]>([]);
  const [loading, setLoading] = useState(true);
  const [cancelling, setCancelling] = useState(false);
  const [finalizing, setFinalizing] = useState(false);
  const [decideId, setDecideId] = useState<string | null>(null);
  const [decideComment, setDecideComment] = useState("");

  const isStudyRole = teacher?.role === "学習担当" || teacher?.role === "寮務部長" || teacher?.role === "寮務課長";

  async function loadAll() {
    setLoading(true);
    try {
      const [t, a] = await Promise.all([
        api.studyTodayAttendees(token!),
        api.absenceRequests(token!),
      ]);
      setToday(t);
      setAbsences(a);
    } catch {
      // ignore
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { loadAll(); }, []);

  async function handleFinalize() {
    if (!confirm("未出席の学生を一括「欠席」にします。よろしいですか？")) return;
    setFinalizing(true);
    try {
      const res = await api.studyFinalize(token!);
      alert(`${res.finalized_count} 名を欠席に確定しました`);
      loadAll();
    } catch {
      alert("エラーが発生しました");
    } finally {
      setFinalizing(false);
    }
  }

  async function handleCancel() {
    if (!confirm("今日の学習を中止します。全員「免除」になります。よろしいですか？")) return;
    setCancelling(true);
    try {
      const res = await api.cancelToday(token!);
      alert(`${res.cancelled_count} 名を免除にしました`);
      loadAll();
    } catch {
      alert("エラーが発生しました");
    } finally {
      setCancelling(false);
    }
  }

  async function handleAbsenceDecide(id: string, decision: "approved" | "rejected") {
    try {
      await api.decideAbsence(id, decision, decideComment || undefined, token!);
      setDecideId(null);
      setDecideComment("");
      loadAll();
    } catch {
      alert("エラーが発生しました");
    }
  }

  const pendingAbsences = absences.filter((a) => a.status === "pending");

  return (
    <div className="p-6 max-w-5xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div>
          <h1 className="text-xl font-bold">学習管理</h1>
          {today && (
            <p className="text-xs text-gray-500 mt-0.5">
              {today.target_date} — 開始 19:40 | 出席 {today.summary.checked_in}/{today.summary.expected} 名
            </p>
          )}
        </div>
        <div className="flex gap-2">
          {isStudyRole && (
            <>
              <button
                onClick={handleFinalize}
                disabled={finalizing}
                className="btn-primary text-xs"
              >
                終了・一括欠席確定
              </button>
              <button
                onClick={handleCancel}
                disabled={cancelling}
                className="btn-ghost text-xs"
              >
                今日学習中止
              </button>
            </>
          )}
          <button onClick={loadAll} className="btn-ghost text-xs">
            更新
          </button>
        </div>
      </div>

      {/* Summary bar */}
      {today && (
        <div className="grid grid-cols-4 gap-3 mb-5">
          {[
            { label: "出席", value: today.summary.checked_in, color: "text-green-600" },
            { label: "遅刻", value: today.summary.late, color: "text-amber-600" },
            { label: "欠席", value: today.summary.absent, color: "text-red-600" },
            { label: "欠席届", value: pendingAbsences.length, color: "text-blue-600" },
          ].map((s) => (
            <div key={s.label} className="card text-center">
              <div className={clsx("text-2xl font-bold", s.color)}>{s.value}</div>
              <div className="text-xs text-gray-500 mt-0.5">{s.label}</div>
            </div>
          ))}
        </div>
      )}

      {/* Tabs */}
      <div className="flex gap-2 mb-4">
        {(["attendance", "absences"] as Tab[]).map((t) => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={clsx(
              "px-4 py-1.5 rounded-full text-sm font-medium transition-colors",
              tab === t
                ? "bg-brand-600 text-white"
                : "text-gray-600 hover:bg-gray-100"
            )}
          >
            {t === "attendance"
              ? `出席一覧`
              : `欠席届 ${pendingAbsences.length > 0 ? `(${pendingAbsences.length})` : ""}`}
          </button>
        ))}
      </div>

      {loading ? (
        <div className="text-center py-12 text-gray-400">読み込み中…</div>
      ) : tab === "attendance" ? (
        /* 出席一覧 */
        <div className="card overflow-hidden p-0">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr>
                <th className="px-4 py-2.5 text-left font-medium text-gray-600">氏名</th>
                <th className="px-4 py-2.5 text-left font-medium text-gray-600">番号</th>
                <th className="px-4 py-2.5 text-left font-medium text-gray-600">部屋</th>
                <th className="px-4 py-2.5 text-left font-medium text-gray-600">状態</th>
                <th className="px-4 py-2.5 text-left font-medium text-gray-600">チェックイン</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {today?.expected_attendees.map((a) => {
                const s = a.checkin?.status ?? (a.expected_status !== "expected" ? "exempt" : "init");
                const { cls, label } = statusColor(s);
                return (
                  <tr key={a.student_id} className="hover:bg-gray-50">
                    <td className="px-4 py-2.5 font-medium">{a.name}</td>
                    <td className="px-4 py-2.5 text-gray-500">{a.student_no}</td>
                    <td className="px-4 py-2.5 text-gray-500">{a.room_no}</td>
                    <td className={clsx("px-4 py-2.5", cls)}>{label}</td>
                    <td className="px-4 py-2.5 text-gray-400 text-xs">
                      {a.checkin?.checked_at
                        ? new Date(a.checkin.checked_at).toLocaleTimeString("ja-JP", {
                            hour: "2-digit",
                            minute: "2-digit",
                          })
                        : a.exemption_reason ?? "—"}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      ) : (
        /* 欠席届一覧 */
        <div className="space-y-3">
          {absences.length === 0 ? (
            <div className="card text-center py-8 text-gray-400">欠席届はありません</div>
          ) : (
            absences.map((a) => (
              <div key={a.id} className="card">
                <div className="flex items-start justify-between">
                  <div>
                    <div className="font-medium">{a.student_id.slice(0, 8)}…</div>
                    <div className="text-xs text-gray-500 mt-0.5">
                      対象日: {a.target_date} | 提出: {new Date(a.submitted_at).toLocaleString("ja-JP")}
                    </div>
                    <div className="text-sm text-gray-700 mt-1">{a.reason}</div>
                  </div>
                  <div className="flex items-center gap-2">
                    <span
                      className={clsx(
                        "text-xs px-2 py-0.5 rounded-full",
                        a.status === "pending"
                          ? "badge-pending"
                          : a.status === "approved"
                          ? "badge-approved"
                          : "badge-rejected"
                      )}
                    >
                      {a.status === "pending" ? "未決" : a.status === "approved" ? "承認" : "拒否"}
                    </span>
                    {a.status === "pending" && isStudyRole && (
                      <button
                        onClick={() => { setDecideId(a.id); setDecideComment(""); }}
                        className="btn-ghost text-xs"
                      >
                        決定する
                      </button>
                    )}
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      )}

      {/* 欠席届 決定モーダル */}
      {decideId && (
        <div
          className="fixed inset-0 bg-black/40 flex items-center justify-center p-4 z-50"
          onClick={(e) => e.target === e.currentTarget && setDecideId(null)}
        >
          <div className="bg-white rounded-2xl shadow-xl w-full max-w-sm p-6">
            <h2 className="text-base font-bold mb-3">欠席届の決定</h2>
            <textarea
              value={decideComment}
              onChange={(e) => setDecideComment(e.target.value)}
              rows={3}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm
                         focus:outline-none focus:ring-2 focus:ring-brand-500 resize-none"
              placeholder="コメント（任意）"
            />
            <div className="flex gap-3 mt-4">
              <button
                onClick={() => handleAbsenceDecide(decideId, "approved")}
                className="btn-primary flex-1"
              >
                承認
              </button>
              <button
                onClick={() => handleAbsenceDecide(decideId, "rejected")}
                className="btn-danger flex-1"
              >
                拒否
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
