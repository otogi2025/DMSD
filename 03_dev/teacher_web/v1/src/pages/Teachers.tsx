/**
 * 教師管理ページ (§3.4)
 * - 教師一覧
 * - 新規招待発行
 */
import { useEffect, useState } from "react";
import { api, type TeacherOut } from "../api/client";
import { useAuth } from "../store/auth";

const ROLES = [
  "寮務部長", "寮務課長", "国際交流部長", "国際交流課長",
  "管理係", "寮監", "学習担当", "寮務一般教师",
];

export default function TeachersPage() {
  const { token, teacher } = useAuth();
  const [teachers, setTeachers] = useState<TeacherOut[]>([]);
  const [loading, setLoading] = useState(true);
  const [showInvite, setShowInvite] = useState(false);
  const [inviteEmail, setInviteEmail] = useState("");
  const [inviteRole, setInviteRole] = useState(ROLES[7]);
  const [inviteDorm, setInviteDorm] = useState<string>("");
  const [inviteResult, setInviteResult] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  const canInvite = ["寮務部長", "寮務課長", "寮監"].includes(teacher?.role ?? "");

  async function load() {
    setLoading(true);
    try {
      const data = await api.listTeachers(token!);
      setTeachers(data);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { load(); }, []);

  async function handleInvite(e: React.FormEvent) {
    e.preventDefault();
    setSubmitting(true);
    setInviteResult(null);
    try {
      const res = await api.createInvitation(
        {
          target_email: inviteEmail,
          target_role: inviteRole,
          target_dorm: inviteDorm ? parseInt(inviteDorm) : undefined,
        },
        token!
      );
      setInviteResult(
        `招待トークン発行済み。登録 URL: /register?token=${res.token} (有効期限: ${new Date(res.expires_at).toLocaleDateString("ja-JP")})`
      );
    } catch (err: unknown) {
      const e = err as { message?: string };
      setInviteResult(`エラー: ${e?.message ?? "不明なエラー"}`);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-xl font-bold">教師管理</h1>
        <div className="flex gap-2">
          {canInvite && (
            <button
              onClick={() => setShowInvite(!showInvite)}
              className="btn-primary text-xs"
            >
              新規招待
            </button>
          )}
          <button onClick={load} className="btn-ghost text-xs">
            更新
          </button>
        </div>
      </div>

      {/* 招待フォーム */}
      {showInvite && (
        <form onSubmit={handleInvite} className="card mb-6 space-y-3">
          <h2 className="font-semibold text-sm">新規教師招待</h2>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1">
                メールアドレス *
              </label>
              <input
                type="email"
                value={inviteEmail}
                onChange={(e) => setInviteEmail(e.target.value)}
                required
                className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm
                           focus:outline-none focus:ring-2 focus:ring-brand-500"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1">
                役職 *
              </label>
              <select
                value={inviteRole}
                onChange={(e) => setInviteRole(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm
                           focus:outline-none focus:ring-2 focus:ring-brand-500"
              >
                {ROLES.map((r) => (
                  <option key={r} value={r}>{r}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1">
                担当寮
              </label>
              <select
                value={inviteDorm}
                onChange={(e) => setInviteDorm(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm
                           focus:outline-none focus:ring-2 focus:ring-brand-500"
              >
                <option value="">指定なし (全寮)</option>
                <option value="1">男寮 (1+2)</option>
                <option value="4">女寮 (4)</option>
              </select>
            </div>
          </div>
          <div className="flex gap-2">
            <button type="submit" disabled={submitting} className="btn-primary text-xs">
              招待発行
            </button>
            <button type="button" onClick={() => setShowInvite(false)} className="btn-ghost text-xs">
              キャンセル
            </button>
          </div>
          {inviteResult && (
            <div className="text-xs bg-gray-50 border border-gray-200 rounded-lg px-3 py-2 break-all">
              {inviteResult}
            </div>
          )}
        </form>
      )}

      {/* 教師一覧 */}
      {loading ? (
        <div className="text-center py-12 text-gray-400">読み込み中…</div>
      ) : (
        <div className="card overflow-hidden p-0">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr>
                <th className="px-4 py-2.5 text-left font-medium text-gray-600">氏名</th>
                <th className="px-4 py-2.5 text-left font-medium text-gray-600">役職</th>
                <th className="px-4 py-2.5 text-left font-medium text-gray-600">担当寮</th>
                <th className="px-4 py-2.5 text-left font-medium text-gray-600">ログイン ID</th>
                <th className="px-4 py-2.5 text-left font-medium text-gray-600">メール</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {teachers.map((t) => (
                <tr key={t.id} className="hover:bg-gray-50">
                  <td className="px-4 py-2.5 font-medium">{t.name}</td>
                  <td className="px-4 py-2.5 text-gray-600">{t.role}</td>
                  <td className="px-4 py-2.5 text-gray-500">
                    {t.assigned_dorm === null ? "全寮" : t.assigned_dorm === 4 ? "女寮" : "男寮"}
                  </td>
                  <td className="px-4 py-2.5 text-gray-500 font-mono">{t.login_id}</td>
                  <td className="px-4 py-2.5 text-gray-400 text-xs">{t.email}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
