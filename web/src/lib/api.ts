export type LoginResponse = {
  message: string;
  user: {
    id: string;
    email: string;
    created_at: string;
  };
  access_token: string;
  token_type: string;
};

const API_BASE_URL: string = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export async function signupRequest(email: string, password: string): Promise<Response> {
  const res: Response = await fetch(`${API_BASE_URL}/auth/signup`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ email, password }),
  });
  return res;
}

export async function loginRequest(email: string, password: string): Promise<LoginResponse> {
  const res: Response = await fetch(`${API_BASE_URL}/auth/login`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ email, password }),
  });

  if (!res.ok) {
    const errorBody: unknown = await res.json();
    console.error("Login failed", errorBody);
    throw new Error("Login failed");
  }

  const data: LoginResponse = await res.json();
  return data;
}

export async function meRequest(token: string): Promise<Response> {
  const res: Response = await fetch(`${API_BASE_URL}/auth/me`, {
    method: "GET",
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
  return res;
}
