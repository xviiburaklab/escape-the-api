import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Escape the API",
  description: "A retro terminal-based API escape room.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
