/** Axios client for labeling tool with JWT auth. */

import axios from "axios";

const API_BASE = import.meta.env.VITE_API_URL
  ? `${import.meta.env.VITE_API_URL}/api/labeling`
  : "/api/labeling";

const labelingApi = axios.create({
  baseURL: API_BASE,
  headers: { "Content-Type": "application/json" },
});

labelingApi.interceptors.request.use((config) => {
  const token = localStorage.getItem("labeling_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

labelingApi.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem("labeling_token");
      localStorage.removeItem("labeling_user");
      window.location.href = "/labeling/login";
    }
    return Promise.reject(error);
  },
);

export default labelingApi;
