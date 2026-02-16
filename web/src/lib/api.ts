
export type LoginResponse = {
  message: string;
  user: {
    id: string;
    email: string;
    created_at: string;
  };
};

export type MeResponse = {
  id: string;
  email: string;
  created_at: string;
};
export type GuardrailDTO = {
  id: string;
  domain: string;
  rule: number;
  is_active: boolean;
}
export type CreateGuardrailDTO = {
  user_id: string;
  domain: string;
  rule: number;
  is_active: boolean;
}
export type GuardrailsResponse ={
  guardrails: GuardrailDTO[];
  count: number;
};
export type ApiFetchOptions = Omit<RequestInit, "credentials"> & {
  retry?: boolean;
}
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
    credentials: "include",
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

export async function meRequest(): Promise<Response> {
  console.log("me request");
  return apiFetch("/auth/me", { method: "GET" });
}


export async function logout(): Promise<Response>{
  return apiFetch("/auth/logout", { method: "POST", retry: false });
} 
export async function guardrailsRequest(): Promise<Response> {
  return apiFetch("/guardrails/", { method: "GET"});
}
export async function addGuardrail(Guardrail: CreateGuardrailDTO): Promise<Response> {
  return apiFetch("/guardrails/", {method: "POST", headers: {
    "Content-Type": "application/json",
  },
  body: JSON.stringify(Guardrail),
  retry: false,
})
}
export async function apiFetch(input: string, init: ApiFetchOptions = {}): Promise<Response> {
  const url: string = input.startsWith("http") ? input : `${API_BASE_URL}${input}`;
  const retry: boolean = init.retry ?? true;

  const res: Response = await fetch(url, {
    ...init,
    credentials: "include",
  });

  if (res.status !== 401 || !retry) return res;

  // Refresh once
  const refreshRes: Response = await fetch(`${API_BASE_URL}/auth/refresh`, {
    method: "POST",
    credentials: "include",
  });

  if (!refreshRes.ok) return res;

  // Retry original request once (disable retry to avoid loops)
  return fetch(url, {
    ...init,
    credentials: "include",
  });
}

 