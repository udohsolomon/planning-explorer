import type { Metadata, Viewport } from "next";
import { DM_Sans, Inter } from "next/font/google";
import "./globals.css";
import { Header } from "@/components/layout/Header";

const dmSans = DM_Sans({
  variable: "--font-dm-sans",
  subsets: ["latin"],
  display: "swap",
});

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
  display: "swap",
});

export const metadata: Metadata = {
  title: "Planning Explorer - AI-Powered Planning Intelligence Platform",
  description: "Discover planning opportunities with our AI-driven analysis of UK planning applications. Access comprehensive data, smart analytics, and actionable insights.",
  keywords: ["planning applications", "UK planning", "AI analytics", "development opportunities", "planning intelligence"],
  authors: [{ name: "Planning Explorer Team" }],
  robots: "index, follow",
  openGraph: {
    type: "website",
    locale: "en_GB",
    url: "https://planningexplorer.ai",
    title: "Planning Explorer - AI-Powered Planning Intelligence",
    description: "Transform planning data into actionable insights with our comprehensive UK planning database and AI analytics.",
    siteName: "Planning Explorer",
  },
  twitter: {
    card: "summary_large_image",
    title: "Planning Explorer - AI-Powered Planning Intelligence",
    description: "Transform planning data into actionable insights with our comprehensive UK planning database and AI analytics.",
  },
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="scroll-smooth" suppressHydrationWarning>
      <body className={`${dmSans.variable} ${inter.variable} antialiased`} suppressHydrationWarning>
        <Header />
        <main className="min-h-screen">
          {children}
        </main>
      </body>
    </html>
  );
}
