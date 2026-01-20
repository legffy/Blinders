"use client";

export default function GoogleButton() {
  const onClick = (): void => {
    window.location.href = `${process.env.NEXT_PUBLIC_API_URL}/auth/google/start`;
  };

  return <button onClick={onClick}>Continue with Google</button>;
}
