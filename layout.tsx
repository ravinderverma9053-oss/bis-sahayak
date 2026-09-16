import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "BIS Sahayak | Compliance guidance",
  description: "Source-grounded BIS standards and compliance guidance prototype.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
