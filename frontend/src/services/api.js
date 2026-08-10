export const BASE =
  import.meta.env.VITE_API_BASE ||
  "https://nexo-bug-hunter.onrender.com";

const DEFAULT_EMAIL = "graj5474@gmail.com";
const DEFAULT_PASSWORD = "Nexo@60752";

let loginPromise = null;

async function loginAutomatically() {
  const savedToken = localStorage.getItem("nexo_token");

  if (savedToken) {
    return savedToken;
  }

  if (!loginPromise) {
    loginPromise = (async () => {
      const response = await fetch(`${BASE}/api/auth/login`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          email: DEFAULT_EMAIL,
          password: DEFAULT_PASSWORD,
        }),
      });

      const data = await response.json().catch(() => ({}));

      if (!response.ok || !data.access_token) {
        throw new Error(
          data.message ||
          data.detail ||
          "Automatic authentication failed."
        );
      }

      localStorage.setItem("nexo_token", data.access_token);

      return data.access_token;
    })().finally(() => {
      loginPromise = null;
    });
  }

  return loginPromise;
}

export async function api(path, options = {}) {
  const token = await loginAutomatically();

  const headers = {
    "Content-Type": "application/json",
    Authorization: `Bearer ${token}`,
    ...(options.headers || {}),
  };

  let response = await fetch(`${BASE}${path}`, {
    ...options,
    headers,
  });

  if (response.status === 401) {
    localStorage.removeItem("nexo_token");

    const newToken = await loginAutomatically();

    response = await fetch(`${BASE}${path}`, {
      ...options,
      headers: {
        ...headers,
        Authorization: `Bearer ${newToken}`,
      },
    });
  }

  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    throw new Error(
      data.message ||
      data.detail ||
      "API request failed."
    );
  }

  return data;
}
