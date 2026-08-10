import { API_BASE } from "../config/constants";

const TOKEN_KEY = "heritia_token";

export function getToken() {
  return localStorage.getItem(TOKEN_KEY);
}

export function setToken(token) {
  localStorage.setItem(TOKEN_KEY, token);
}

export function clearToken() {
  localStorage.removeItem(TOKEN_KEY);
}

async function request(path, options = {}) {
  const headers = {
    "Content-Type": "application/json",
    ...(options.headers || {}),
  };
  const token = getToken();
  if (token) headers.Authorization = `Bearer ${token}`;

  const res = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers,
  });

  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    const message = data.detail || data.message || "Request failed";
    throw new Error(typeof message === "string" ? message : JSON.stringify(message));
  }
  return data;
}

export const api = {
  register: (body) => request("/auth/register", { method: "POST", body: JSON.stringify(body) }),
  login: (body) => request("/auth/login", { method: "POST", body: JSON.stringify(body) }),
  forgotPassword: (body) =>
    request("/auth/forgot-password", { method: "POST", body: JSON.stringify(body) }),
  resetPassword: (body) =>
    request("/auth/reset-password", { method: "POST", body: JSON.stringify(body) }),
  socialLogin: (body) => request("/auth/social", { method: "POST", body: JSON.stringify(body) }),
  getMe: () => request("/profil/me"),
  updateMe: (body) => request("/profil/me", { method: "PATCH", body: JSON.stringify(body) }),
  updateGoldBadges: (count) =>
    request("/profil/me/gold-badges", {
      method: "PATCH",
      body: JSON.stringify({ gold_badges_count: count }),
    }),
  listRecipes: () => request("/recettes"),
  createRecipe: (body) => request("/recettes", { method: "POST", body: JSON.stringify(body) }),
  stripeOnboarding: () => request("/marketplace/stripe/onboarding", { method: "POST" }),
  listEbooks: () => request("/marketplace/ebooks"),
  listMyEbooks: () => request("/marketplace/ebooks/mine"),
  createEbook: (body) =>
    request("/marketplace/ebooks", { method: "POST", body: JSON.stringify(body) }),
  checkoutEbook: (ebook_listing_id) =>
    request("/marketplace/checkout", {
      method: "POST",
      body: JSON.stringify({ ebook_listing_id }),
    }),
};