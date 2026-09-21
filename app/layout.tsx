import type { Metadata } from "next";
import type { ReactNode } from "react";
import "./globals.css";

export const metadata: Metadata = {
  title: "FactLens 팩트렌즈 | 원문과 근거를 한눈에",
  description: "주장과 출처를 비교해 더 나은 판단을 돕는 팩트체크 워크스페이스입니다.",
};

export default function RootLayout({ children }: {children: ReactNode}) {
  return (
    <html lang="ko">
      <body>{children}</body>
    </html>
  );
}
