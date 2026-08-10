import { createContext, useContext, useEffect, useState } from "react";
import { api, clearToken, getToken, setToken } from "../services/api";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [booting, setBooting] = useState(true);
  const [splashDone, setSplashDone] = useState(false);

  useEffect(() => {
    const t = setTimeout(() => setSplashDone(true), 2200);
    return () => clearTimeout(t);
  }, []);

  useEffect(() => {
    async function boot() {
      const token = getToken();
      if (!token) {
        setBooting(false);
        return;
      }
      try {
        const me = await api.getMe();
        setUser(me);
      } catch {
        clearToken();
      } finally {
        setBooting(false);
      }
    }
    boot();
  }, []);

  async function loginWithToken(token) {
    setToken(token);
    const me = await api.getMe();
    setUser(me);
    return me;
  }

  async function logout() {
    clearToken();
    setUser(null);
  }

  async function refreshUser() {
    const me = await api.getMe();
    setUser(me);
    return me;
  }

  return (
    <AuthContext.Provider
      value={{
        user,
        setUser,
        booting,
        splashDone,
        isAuthenticated: Boolean(user),
        loginWithToken,
        logout,
        refreshUser,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}