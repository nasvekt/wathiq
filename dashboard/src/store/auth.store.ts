import { create } from 'zustand';
import type { User } from '@/types/employee';

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  setAuth: (user: User, token: string) => void;
  setUser: (user: User) => void;
  logout: () => void;
  setLoading: (loading: boolean) => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  token: localStorage.getItem('wathiq_token'),
  isAuthenticated: !!localStorage.getItem('wathiq_token'),
  isLoading: false,
  setAuth: (user, token) => {
    localStorage.setItem('wathiq_token', token);
    localStorage.setItem('wathiq_company_id', user.company_id);
    set({ user, token, isAuthenticated: true });
  },
  setUser: (user) => set({ user }),
  logout: () => {
    localStorage.removeItem('wathiq_token');
    localStorage.removeItem('wathiq_company_id');
    set({ user: null, token: null, isAuthenticated: false });
  },
  setLoading: (loading) => set({ isLoading: loading }),
}));
