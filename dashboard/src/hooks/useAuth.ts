import { useMutation } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { authApi } from '@/services/api';
import { useAuthStore } from '@/store/auth.store';
import type { AxiosError } from 'axios';

interface LoginCredentials {
  email: string;
  password: string;
}

interface RegisterData {
  email: string;
  password: string;
  company_name: string;
  industry: string;
  company_size: string;
}

export function useLogin() {
  const setAuth = useAuthStore((s) => s.setAuth);
  const setLoading = useAuthStore((s) => s.setLoading);
  const navigate = useNavigate();

  return useMutation({
    mutationFn: async (credentials: LoginCredentials) => {
      const response = await authApi.login(credentials.email, credentials.password);
      return response.data;
    },
    onMutate: () => setLoading(true),
    onSuccess: (data) => {
      setAuth(data.user, data.token);
      navigate('/');
    },
    onSettled: () => setLoading(false),
  });
}

export function useRegister() {
  const navigate = useNavigate();

  return useMutation({
    mutationFn: async (data: RegisterData) => {
      const response = await authApi.register(data);
      return response.data;
    },
    onSuccess: () => {
      navigate('/onboarding');
    },
    onError: (error: AxiosError) => {
      console.error('Registration failed:', error);
    },
  });
}

export function useLogout() {
  const logout = useAuthStore((s) => s.logout);
  const navigate = useNavigate();

  return () => {
    logout();
    navigate('/login');
  };
}
