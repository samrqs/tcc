import { config } from "@/lib/config";
import { deleteCookie, getCookie, setCookie } from "@/lib/cookies";
import { createContext, ReactNode, useEffect, useState } from "react";

export interface User {
  id: number;
  email: string;
  name: string;
  phone: string;
}

export interface LoginResult {
  success: boolean;
  error?: string;
}

export interface AuthContextType {
  user: User | null;
  accessToken: string | null;
  refreshToken: string | null;
  login: (email: string, password: string) => Promise<LoginResult>;
  logout: () => void;
  isLoading: boolean;
}

export const AuthContext = createContext<AuthContextType | undefined>(
  undefined
);

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider = ({ children }: AuthProviderProps) => {
  const [user, setUser] = useState<User | null>(null);
  const [accessToken, setAccessToken] = useState<string | null>(null);
  const [refreshToken, setRefreshToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Carrega dados dos cookies na inicialização
  useEffect(() => {
    const storedUser = getCookie("user");
    const storedAccessToken = getCookie("accessToken");
    const storedRefreshToken = getCookie("refreshToken");

    if (storedUser && storedAccessToken && storedRefreshToken) {
      try {
        setUser(JSON.parse(storedUser));
        setAccessToken(storedAccessToken);
        setRefreshToken(storedRefreshToken);
      } catch (error) {
        console.error("Erro ao carregar dados dos cookies:", error);
        // Se houver erro ao parsear, limpa os cookies
        deleteCookie("user");
        deleteCookie("accessToken");
        deleteCookie("refreshToken");
      }
    }
    setIsLoading(false);
  }, []);

  // Função para fazer login
  const login = async (
    email: string,
    password: string
  ): Promise<LoginResult> => {
    try {
      const response = await fetch(`${config.api.baseUrl}/auth/token/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          email,
          password,
        }),
      });

      if (response.ok) {
        const data = await response.json();

        // Salva os dados no estado e cookies
        setUser(data.user);
        setAccessToken(data.access);
        setRefreshToken(data.refresh);

        // Salva nos cookies com expiração de 7 dias
        setCookie("user", JSON.stringify(data.user), 7);
        setCookie("accessToken", data.access, 7);
        setCookie("refreshToken", data.refresh, 30); // refresh token com mais tempo

        return { success: true };
      } else {
        const errorData = await response.json();

        if (response.status === 401) {
          return { success: false, error: "Email ou senha incorretos." };
        } else if (errorData.detail) {
          return { success: false, error: errorData.detail };
        } else if (
          errorData.non_field_errors &&
          Array.isArray(errorData.non_field_errors)
        ) {
          return { success: false, error: errorData.non_field_errors[0] };
        } else {
          return {
            success: false,
            error: "Erro ao fazer login. Tente novamente.",
          };
        }
      }
    } catch (error) {
      console.error("Erro no login:", error);
      return {
        success: false,
        error: "Erro de conexão. Verifique sua internet e tente novamente.",
      };
    }
  };

  // Função para fazer logout
  const logout = () => {
    setUser(null);
    setAccessToken(null);
    setRefreshToken(null);

    // Remove os cookies
    deleteCookie("user");
    deleteCookie("accessToken");
    deleteCookie("refreshToken");
  };

  // Função para renovar o token (pode ser útil para futuras implementações)
  const refreshAccessToken = async (): Promise<boolean> => {
    if (!refreshToken) return false;

    try {
      const response = await fetch(
        `${config.api.baseUrl}/auth/token/refresh/`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            refresh: refreshToken,
          }),
        }
      );

      if (response.ok) {
        const data = await response.json();
        setAccessToken(data.access);
        setCookie("accessToken", data.access, 7);
        return true;
      }
      return false;
    } catch (error) {
      console.error("Erro ao renovar token:", error);
      return false;
    }
  };

  const value = {
    user,
    accessToken,
    refreshToken,
    login,
    logout,
    isLoading,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
