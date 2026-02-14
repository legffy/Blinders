"use client";

import {JSX} from "react";
import { useRouter } from 'next/navigation';
export default function SettingsPage(): JSX.Element {
    const router = useRouter();
    return (<div className="flex flex-col"><h1 className="text-xl">Settings</h1>
    <button className="border-2 w-fit" onClick={()=>{router.push('/dashboard')}}>Dashboard</button>
    </div>)
}