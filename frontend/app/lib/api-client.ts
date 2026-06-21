import axios from "axios";
import { tokenStorage } from "@/lib/auth/token";

export const api = axios.create({
  baseURL: "http://localhost:8000/api",
});

// ------------------------------
// Attach access token
// ------------------------------
api.interceptors.request.use((config) => {
  const token = tokenStorage.getAccess();

  if (token && config.headers) {
    config.headers.Authorization = `Bearer ${token}`;
  }

  return config;
});

// ------------------------------
// Refresh logic control
// ------------------------------
let isRefreshing = false;
let failedQueue: any[] = [];

const processQueue = (error: any, token: string | null = null) => {
  failedQueue.forEach((prom) => {
    if (error) {
      prom.reject(error);
    } else {
      prom.resolve(token);
    }
  });

  failedQueue = [];
};

// ------------------------------
// Response interceptor (core logic)
// ------------------------------
api.interceptors.response.use(
  (response) => response,

  async (error) => {
    const originalRequest = error.config;

    // If no response or not 401 → just throw
    if (!error.response || error.response.status !== 401) {
      return Promise.reject(error);
    }

    const refreshToken = tokenStorage.getRefresh();

    // If no refresh token → logout hard
    if (!refreshToken) {
      tokenStorage.clear();
      return Promise.reject(error);
    }

    // Prevent infinite loop
    if (originalRequest._retry) {
      tokenStorage.clear();
      return Promise.reject(error);
    }

    originalRequest._retry = true;

    // If already refreshing → queue request
    if (isRefreshing) {
      return new Promise((resolve, reject) => {
        failedQueue.push({ resolve, reject });
      }).then((token) => {
        originalRequest.headers.Authorization = "Bearer " + token;
        return api(originalRequest);
      });
    }

    isRefreshing = true;

    try {
      const res = await axios.post(
        "http://localhost:8000/api/auth/token/refresh/",
        {
          refresh: refreshToken,
        }
      );

      const newAccessToken = res.data.access;

      // update storage
      const oldRefresh = tokenStorage.getRefresh();
      if (oldRefresh) {
        tokenStorage.setTokens(newAccessToken, oldRefresh);
      }

      api.defaults.headers.common.Authorization = `Bearer ${newAccessToken}`;

      processQueue(null, newAccessToken);

      originalRequest.headers.Authorization = `Bearer ${newAccessToken}`;

      return api(originalRequest);
    } catch (err) {
      processQueue(err, null);
      tokenStorage.clear();
      return Promise.reject(err);
    } finally {
      isRefreshing = false;
    }
  }
);