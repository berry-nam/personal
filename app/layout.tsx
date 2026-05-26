import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "재무계정 분류 검토 · Financial Taxonomy Review",
  description: "Korean DART financial account → IFRS canonical ID review tool",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ko">
      <body>{children}</body>
    </html>
  );
}
