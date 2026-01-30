"use client";

import { FormEvent, useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { loginRequest, LoginResponse, meRequest } from "@/lib/api";
import type { MeResponse } from "@/lib/api";
import { JSX } from "react";
import  GoogleButton  from "../components/GoogleButton"

export default function LoginPage(): JSX.Element {
  const [email, setEmail] = useState<string>("");
  const [password, setPassword] = useState<string>("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(false);

  const router = useRouter();
  useEffect(() => {
    async function fetchMe(): Promise<void> {
      try {
        const res = await meRequest();
        const data = await res.json();

        if (!res.ok) {
          setError(data.detail ?? "Failed to fetch user");
        } else {
          router.push('/dashboard')
        }
      } catch (err) {
        setError("Request failed");
      } finally {
        setLoading(false);
      }
    }

    void fetchMe();
  }, []);
  
  async function handleSubmit(e: FormEvent<HTMLFormElement>): Promise<void> {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      await loginRequest(email, password);
      router.push("/dashboard");
    } catch (err) {
      setError("Invalid email or password");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="flex min-h-screen items-center justify-center">
      <form onSubmit={handleSubmit} className="flex flex-col gap-2 w-80">
        <h1 className="text-xl font-bold">Login</h1>

        <input
          className="border px-2 py-1 rounded"
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="email"
          required
        />

        <input
          className="border px-2 py-1 rounded"
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder="password"
          required
        />

        <button
          type="submit"
          className="border px-2 py-1 rounded"
          disabled={loading}
        >
          {loading ? "Logging in..." : "Login"}
        </button>
        <GoogleButton/>
        {error && <p className="text-red-600 text-sm">{error === "Missing access_token cookie" ? "" : error }</p>}
      </form>
    </main>
  );
}
