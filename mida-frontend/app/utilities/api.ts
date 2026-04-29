const BASE_URL = "http://localhost:8000";

// --- Auth ---
export async function login(username: string, password: string) {
  const response = await fetch(`${BASE_URL}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password }),
  });
  if (!response.ok) throw new Error("Login fejlede");
  return response.json();
}

// --- Data ---
export async function getData(
  sourceName: string,
  page: number = 1,
  limit: number = 2
) {
  const response = await fetch(
    `${BASE_URL}/data/${sourceName}?page=${page}&limit=${limit}`,
    {
      headers: {
        Authorization: `Bearer ${getToken()}`,
      },
    }
  );
  if (!response.ok) throw new Error(`Kunne ikke hente data for '${sourceName}'`);
  return response.json();
}

// --- Token helpers ---
export function getToken(): string | null {
  return localStorage.getItem("token");
}

export function setToken(token: string): void {
  localStorage.setItem("token", token);
}

export function removeToken(): void {
  localStorage.removeItem("token");
}

export function isLoggedIn(): boolean {
  return getToken() !== null;
}