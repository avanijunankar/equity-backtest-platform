"use client";

import { useEffect, useState } from "react";
import { useTheme } from "next-themes";
import { AppShell } from "@/components/layout/app-shell";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { checkHealth } from "@/lib/api";

export default function SettingsPage() {
  const { theme, setTheme } = useTheme();
  const [dataSource, setDataSource] = useState("demo");
  const [apiUrl, setApiUrl] = useState("");

  useEffect(() => {
    checkHealth().then((h) => setDataSource(h.data_source));
    setApiUrl(process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000");
  }, []);

  return (
    <AppShell dataSource={dataSource}>
      <h2 className="mb-6 text-2xl font-bold">Settings</h2>
      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Appearance</CardTitle>
          </CardHeader>
          <CardContent className="flex gap-2">
            <Button variant={theme === "light" ? "default" : "outline"} onClick={() => setTheme("light")}>
              Light
            </Button>
            <Button variant={theme === "dark" ? "default" : "outline"} onClick={() => setTheme("dark")}>
              Dark
            </Button>
            <Button variant={theme === "system" ? "default" : "outline"} onClick={() => setTheme("system")}>
              System
            </Button>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>API Configuration</CardTitle>
          </CardHeader>
          <CardContent className="text-sm text-slate-500">
            <p>Backend URL: {apiUrl}</p>
            <p className="mt-2">Edit NEXT_PUBLIC_API_URL in frontend/.env.local to change.</p>
          </CardContent>
        </Card>
      </div>
    </AppShell>
  );
}
