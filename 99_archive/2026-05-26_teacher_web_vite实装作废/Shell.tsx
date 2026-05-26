import type { ReactNode } from "react";
import { useAuth } from "../store/auth";

type Page = "applications" | "study" | "rollcall" | "teachers";

interface Props {
  children: ReactNode;
  currentPage: Page;
  onNavigate: (p: Page) => void;
}

const NAV_ITEMS: { id: Page; label: string; icon: string }[] = [
  { id: "applications", label: "出寮届承認", icon: "📋" },
  { id: "study",        label: "学習",       icon: "📚" },
  { id: "rollcall",     label: "点呼",       icon: "✅" },
  { id: "teachers",     label: "教師管理",   icon: "👥" },
];

export default function Shell({ children, currentPage, onNavigate }: Props) {
  const { teacher, logout } = useAuth();

  return (
    <div className="min-h-screen flex">
      {/* Sidebar */}
      <aside className="w-56 bg-gray-900 text-white flex flex-col">
        {/* Logo */}
        <div className="px-4 py-5 border-b border-gray-700">
          <div className="flex items-center gap-2">
            <span className="text-xl">灯</span>
            <div>
              <div className="font-bold text-base leading-none">Tomoshibi</div>
              <div className="text-xs text-gray-400 mt-0.5">教師ダッシュボード</div>
            </div>
          </div>
        </div>

        {/* Nav */}
        <nav className="flex-1 px-2 py-4 space-y-1">
          {NAV_ITEMS.map((item) => (
            <button
              key={item.id}
              onClick={() => onNavigate(item.id)}
              className={[
                "w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors",
                currentPage === item.id
                  ? "bg-brand-600 text-white"
                  : "text-gray-300 hover:bg-gray-700 hover:text-white",
              ].join(" ")}
            >
              <span>{item.icon}</span>
              {item.label}
            </button>
          ))}
        </nav>

        {/* Teacher info + logout */}
        <div className="px-4 py-4 border-t border-gray-700">
          <div className="text-xs text-gray-400 truncate">{teacher?.name}</div>
          <div className="text-xs text-gray-500 truncate">{teacher?.role}</div>
          <button
            onClick={logout}
            className="mt-2 text-xs text-gray-400 hover:text-white transition-colors"
          >
            ログアウト
          </button>
        </div>
      </aside>

      {/* Main */}
      <main className="flex-1 overflow-auto">
        {children}
      </main>
    </div>
  );
}
