/**
 * 出寮届承認ページ (#10-#13)
 * 自分の役職 (role) が承認待ちの届一覧 → 承認/拒否モーダル
 */
import { useEffect, useState } from "react";
import { api, type Application } from "../api/client";
import { useAuth } from "../store/auth";
import clsx from "clsx";

function statusBadge(status: string) {
  const map: Record<string, string> = {
    pending: "badge-pending",
    approved_partial: "badge-partial",
    approved: "badge-approved",
    rejected: "badge-rejected",
    withdrawn: "bg-gray-100 text-gray-600 inline-flex px-2 py-0.5 rounded-full text-xs font-medium",
  };
  const label: Record<string, string> = {
    pending: "承認待ち",
    approved_partial: "一部承認",
    approved: "承認済",
    rejected: "拒否",
    withdrawn: "取り下げ",
  };
  return (
    <span className={map[status] ?? "badge-pending"}>
      {label[status] ?? status}
    </span>
  );
}

export default function ApplicationsPage() {
  const { token } = useAuth();
  const [apps, setApps] = useState<Application[]>([]);
  const [loading, setLoading] = useState(true);
  const [selected, setSelected] = useState<Application | null>(null);
  const [comment, setComment] = useState("");
  const [deciding, setDeciding] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function load() {
    setLoading(true);
    try {
      const data = await api.pendingForMe(token!);
      setApps(data);
    } catch {
      // ignore
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { load(); }, []);

  async function decide(decision: "approve" | "reject") {
    if (!selected || !token) return;
    setDeciding(true);
    setError(null);
    try {
      await api.decide(selected.id, decision, comment || undefined, token);
      setSelected(null);
      setComment("");
      load();
    } catch (e: unknown) {
      const err = e as { message?: string };
      setError(err?.message ?? "エラーが発生しました");
    } finally {
      setDeciding(false);
    }
  }

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-xl font-bold">出寮届 承認</h1>
          <p className="text-xs text-gray-500 mt-0.5">
            あなたの役職が承認待ちの届 {apps.length} 件
          </p>
        </div>
        <button onClick={load} className="btn-ghost text-xs">
          更新
        </button>
      </div>

      {loading ? (
        <div className="text-center py-12 text-gray-400">読み込み中…</div>
      ) : apps.length === 0 ? (
        <div className="card text-center py-12 text-gray-400">
          承認待ちの届はありません
        </div>
      ) : (
        <div className="space-y-3">
          {apps.map((app) => (
            <div
              key={app.id}
              className="card cursor-pointer hover:shadow-md transition-shadow"
              onClick={() => { setSelected(app); setComment(""); setError(null); }}
            >
              <div className="flex items-start justify-between gap-4">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="font-semibold">
                      {app.student?.name ?? "—"}
                    </span>
                    <span className="text-xs text-gray-500">
                      {app.student?.student_no}
                    </span>
                    <span className="text-xs text-gray-400">
                      {app.student?.room_no}
                    </span>
                  </div>
                  <div className="flex items-center gap-3 text-xs text-gray-600">
                    <span className="font-medium">{app.kind}</span>
                    <span>
                      {app.leave_date} → {app.return_date}
                    </span>
                  </div>
                </div>
                <div className="shrink-0">
                  {statusBadge(app.status)}
                </div>
              </div>

              {/* Chain */}
              <div className="mt-3 flex flex-wrap gap-2">
                {app.approval_chain.map((step, i) => (
                  <div
                    key={i}
                    className={clsx(
                      "text-xs px-2 py-1 rounded border",
                      step.decision === "approve"
                        ? "border-green-300 bg-green-50 text-green-700"
                        : step.decision === "reject"
                        ? "border-red-300 bg-red-50 text-red-700"
                        : "border-gray-200 bg-gray-50 text-gray-500"
                    )}
                  >
                    {step.approver_role}
                    {step.decision === "approve" && " ✓"}
                    {step.decision === "reject" && " ✗"}
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* 承認モーダル */}
      {selected && (
        <div
          className="fixed inset-0 bg-black/40 flex items-center justify-center p-4 z-50"
          onClick={(e) => e.target === e.currentTarget && setSelected(null)}
        >
          <div className="bg-white rounded-2xl shadow-xl w-full max-w-lg p-6">
            <h2 className="text-lg font-bold mb-1">
              {selected.kind} — {selected.student?.name}
            </h2>
            <div className="text-xs text-gray-500 mb-4">
              {selected.leave_date} {selected.leave_time} →{" "}
              {selected.return_date} {selected.return_time}
            </div>

            {/* Chain */}
            <div className="mb-4 space-y-1">
              {selected.approval_chain.map((step, i) => (
                <div key={i} className="flex items-center gap-2 text-xs">
                  <span className="w-28 shrink-0 font-medium text-gray-700">
                    {step.approver_role}
                  </span>
                  <span
                    className={clsx(
                      "px-2 py-0.5 rounded",
                      step.decision === "approve"
                        ? "bg-green-100 text-green-700"
                        : step.decision === "reject"
                        ? "bg-red-100 text-red-700"
                        : "bg-gray-100 text-gray-500"
                    )}
                  >
                    {step.decision === "approve"
                      ? "承認"
                      : step.decision === "reject"
                      ? "拒否"
                      : "未決"}
                  </span>
                  {step.comment && (
                    <span className="text-gray-400 truncate">"{step.comment}"</span>
                  )}
                </div>
              ))}
            </div>

            <label className="block text-xs font-medium text-gray-700 mb-1">
              コメント（任意）
            </label>
            <textarea
              value={comment}
              onChange={(e) => setComment(e.target.value)}
              rows={3}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm
                         focus:outline-none focus:ring-2 focus:ring-brand-500 resize-none"
              placeholder="学生に伝えるコメントがあれば…"
            />

            {error && (
              <div className="mt-2 text-xs text-red-600 bg-red-50 px-3 py-2 rounded">
                {error}
              </div>
            )}

            <div className="flex gap-3 mt-4">
              <button
                onClick={() => decide("approve")}
                disabled={deciding}
                className="btn-primary flex-1"
              >
                承認
              </button>
              <button
                onClick={() => decide("reject")}
                disabled={deciding}
                className="btn-danger flex-1"
              >
                拒否
              </button>
              <button
                onClick={() => setSelected(null)}
                className="btn-ghost"
              >
                キャンセル
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
