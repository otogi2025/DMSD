import { useAuth } from "./store/auth";
import LoginPage from "./pages/Login";
import Shell from "./components/Shell";
import { useState } from "react";
import ApplicationsPage from "./pages/Applications";
import StudyPage from "./pages/Study";
import RollCallPage from "./pages/RollCall";
import TeachersPage from "./pages/Teachers";

type Page = "applications" | "study" | "rollcall" | "teachers";

export default function App() {
  const { isLoggedIn } = useAuth();
  const [page, setPage] = useState<Page>("applications");

  if (!isLoggedIn()) return <LoginPage />;

  return (
    <Shell currentPage={page} onNavigate={setPage}>
      {page === "applications" && <ApplicationsPage />}
      {page === "study" && <StudyPage />}
      {page === "rollcall" && <RollCallPage />}
      {page === "teachers" && <TeachersPage />}
    </Shell>
  );
}
