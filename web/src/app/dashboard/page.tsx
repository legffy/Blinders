"use client";

import { useEffect, useState } from "react";
import { meRequest } from "@/lib/api";
import {JSX} from "react";

type MeResponse = {
  id: string;
  email: string;
  created_at: string;
};

export default function DashboardPage(): JSX.Element {
  const [me, setMe] = useState<MeResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    async function fetchMe(): Promise<void> {
      const token: string | null = localStorage.getItem("access_token");
      if (!token) {
        setError("No token found. Please log in.");
        setLoading(false);
        return;
      }

      try {
        const res = await meRequest(token);
        const data = await res.json();

        if (!res.ok) {
          setError(data.detail ?? "Failed to fetch user");
        } else {
          setMe(data as MeResponse);
        }
      } catch (err) {
        setError("Request failed");
      } finally {
        setLoading(false);
      }
    }

    void fetchMe();
  }, []);

  if (loading) {
    return <main className="p-4">Loading...</main>;
  }

  if (error) {
    return <main className="p-4 text-red-600">{error}</main>;
  }

  if (!me) {
    return <main className="p-4">No user data.</main>;
  }

  return (
    <main className="p-4">
      <h1 className="text-xl font-bold mb-2">Dashboard</h1>
      <p>Email: {me.email}</p>
      <p>User ID: {me.id}</p>
      <p>Created at: {me.created_at}</p>
    </main>
  );
}
