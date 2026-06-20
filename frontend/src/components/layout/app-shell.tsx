"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  BarChart3,
  Database,
  GitCompare,
  LayoutDashboard,
  Moon,
  Settings,
  SlidersHorizontal,
  Sun,
  TrendingUp,
} from "lucide-react";
import { useTheme } from "next-themes";
import { useEffect, useState } from "react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

const nav = [
  { href: "/", label: "Dashboard", icon: LayoutDashboard },
  { href: "/builder", label: "Strategy Builder", icon: SlidersHorizontal },
  { href: "/results", label: "Results", icon: BarChart3 },
  { href: "/compare", label: "Compare", icon: GitCompare },
  { href: "/data", label: "Data", icon: Database },
  { href: "/settings", label: "Settings", icon: Settings },
];

export function AppShell({
  children,
  dataSource,
}: {
  children: React.ReactNode;
  dataSource?: string;
}) {
  const pathname = usePathname();
  const { theme, setTheme } = useTheme();
  const [mounted, setMounted] = useState(false);
  useEffect(() => setMounted(true), []);

  return (
    <div className="flex min-h-screen bg-slate-50 dark:bg-slate-950">
      <aside className="hidden w-64 flex-col border-r border-slate-200 bg-white dark:border-slate-800 dark:bg-slate-900 md:flex">
        <div className="flex items-center gap-2 border-b border-slate-200 p-5 dark:border-slate-800">
          <TrendingUp className="h-7 w-7 text-indigo-600" />
          <div>
            <p className="font-bold text-slate-900 dark:text-white">EquityBacktest</p>
            <p className="text-xs text-slate-500">Indian Equities</p>
          </div>
        </div>
        <nav className="flex-1 space-y-1 p-3">
          {nav.map(({ href, label, icon: Icon }) => (
            <Link
              key={href}
              href={href}
              className={cn(
                "flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors",
                pathname === href
                  ? "bg-indigo-50 text-indigo-700 dark:bg-indigo-950 dark:text-indigo-300"
                  : "text-slate-600 hover:bg-slate-100 dark:text-slate-400 dark:hover:bg-slate-800"
              )}
            >
              <Icon className="h-4 w-4" />
              {label}
            </Link>
          ))}
        </nav>
        <div className="border-t border-slate-200 p-4 dark:border-slate-800">
          <Badge variant={dataSource === "demo" ? "demo" : "success"}>
            {dataSource === "demo" ? "Demo Mode" : dataSource || "Live DB"}
          </Badge>
        </div>
      </aside>

      <div className="flex flex-1 flex-col">
        <header className="flex items-center justify-between border-b border-slate-200 bg-white px-4 py-3 dark:border-slate-800 dark:bg-slate-900 md:px-6">
          <h1 className="text-lg font-semibold text-slate-900 dark:text-white md:hidden">EquityBacktest</h1>
          <div className="ml-auto flex items-center gap-2">
            <Badge variant={dataSource === "demo" ? "demo" : "success"} className="hidden md:inline-flex">
              {dataSource === "demo" ? "Demo Data" : "PostgreSQL"}
            </Badge>
            <Button
              variant="ghost"
              size="icon"
              onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
              aria-label="Toggle theme"
            >
              {mounted ? (
                theme === "dark" ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />
              ) : (
                <span className="h-4 w-4" />
              )}
            </Button>
          </div>
        </header>
        <main className="flex-1 p-4 md:p-6">{children}</main>
      </div>
    </div>
  );
}
