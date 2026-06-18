"use client";

import { useState, useEffect } from "react";
import { tokenStorage } from "./token";
import { api } from "@/lib/api/client";

export function useAuth() {
  const [user, setUser] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  // Hydrate user on refresh
  useEffect(() => {
    const access = tokenStorage.getAccess();

    if (!access) {
      setLoading(false);
      return;
    }

    // Optional: we already get user from login response
    const storedUser = localStorage.getItem("user");

    if (storedUser) {
      setUser(JSON.parse(storedUser));
    }

    setLoading(false);
  }, []);

  const login = async (email: string, password: string) => {
    const res = await api.post("/auth/token/", {
      email,
      password,
    });

    const { access, refresh, user } = res.data;

    tokenStorage.setTokens(access, refresh);
    localStorage.setItem("user", JSON.stringify(user));

    setUser(user);

    return user;
  };

  const logout = () => {
    tokenStorage.clear();
    localStorage.removeItem("user");
    setUser(null);
  };

  return {
    user,
    loading,
    login,
    logout,
    isAuthenticated: !!user,
  };
}