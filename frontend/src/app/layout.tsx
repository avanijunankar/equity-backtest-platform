import type { Metadata } from "next";
import localFont from "next/font/local";
import { Toaster } from "sonner";
import { ThemeProvider } from "@/components/theme-provider";
import { BacktestProvider } from "@/context/backtest-context";
import "./globals.css";

const geistSans = localFont({
  src: "./fonts/GeistVF.woff",
  variable: "--font-geist-sans",
  weight: "100 900",
});

export const metadata: Metadata = {
  title: "Equity Backtest Platform",
  description: "Production-grade fundamental strategy backtesting for Indian equities",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={`${geistSans.variable} font-sans antialiased`}>
        <ThemeProvider attribute="class" defaultTheme="system" enableSystem>
          <BacktestProvider>
            {children}
            <Toaster richColors position="top-right" />
          </BacktestProvider>
        </ThemeProvider>
      </body>
    </html>
  );
}
