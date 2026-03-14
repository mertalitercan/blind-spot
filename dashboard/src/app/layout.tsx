import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "BlindSpot — Fraud Detection Dashboard",
  description: "Multi-agent fraud detection monitoring",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="bg-[#050510] text-[#E2E8F0] min-h-screen antialiased">
        {children}
      </body>
    </html>
  );
}
