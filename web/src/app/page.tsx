"use client";
import Image from "next/image";
import React, { useEffect, useState } from "react";

type HealthResponse = { status: string };

export default function Home(): React.JSX.Element {
  const [health, setHealth] = useState<string>("not ok");

  async function testHealth(): Promise<void> {
    try {
      const baseUrl: string =
        process.env.NEXT_PUBLIC_API_URL ??
        (() => {
          throw new Error("Missing NEXT_PUBLIC_API_URL (set it in web/.env.local)");
        })();

      const res: Response = await fetch(`${baseUrl}/`, { cache: "no-store" });
      if (!res.ok) {
        const text: string = await res.text().catch(() => "");
        throw new Error(`Health failed: ${res.status} ${text}`);
      }

      const data: HealthResponse = (await res.json()) as HealthResponse;
      setHealth(data.status);
    } catch (err) {
      console.error("Failed to get health endpoint:", err);
      setHealth("error");
    }
  }

  useEffect(() => { void testHealth(); }, []);

  return (
    <div className="font-sans grid grid-rows-[20px_1fr_20px] items-center justify-items-center min-h-screen p-8 pb-20 gap-16 sm:p-20">
      <main className="flex flex-col gap-[32px] row-start-2 items-center sm:items-start">
        <h1 className="text-5xl">health is: {health}</h1>
        {/* ...rest of your JSX unchanged... */}
        <Image className="dark:invert" src="/next.svg" alt="Next.js logo" width={180} height={38} priority />
      </main>
    </div>
  );
}
