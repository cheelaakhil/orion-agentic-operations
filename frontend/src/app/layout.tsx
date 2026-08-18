import "./globals.css";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "ORION — AI Business Operations Intelligence System",
  description: "Executive Command Center: Detect, Investigate, Recommend, and Govern Consequential Business Operations.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="bg-[#090D16] text-slate-100 min-h-screen antialiased selection:bg-cyan-500/30 selection:text-cyan-200">
        {children}
      </body>
    </html>
  );
}
