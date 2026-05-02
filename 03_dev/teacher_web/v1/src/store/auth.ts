import { create } from "zustand";
import { persist } from "zustand/middleware";

export interface TeacherProfile {
  id: string;
  login_id: string;
  name: string;
  email: string;
  role: string;
  assigned_dorm: number | null;
  status: string;
  created_at: string;
}

interface AuthState {
  token: string | null;
  teacher: TeacherProfile | null;
  login: (token: string, teacher: TeacherProfile) => void;
  logout: () => void;
  isLoggedIn: () => boolean;
}

export const useAuth = create<AuthState>()(
  persist(
    (set, get) => ({
      token: null,
      teacher: null,
      login: (token, teacher) => set({ token, teacher }),
      logout: () => set({ token: null, teacher: null }),
      isLoggedIn: () => get().token !== null,
    }),
    { name: "tomoshibi-teacher-auth" }
  )
);
