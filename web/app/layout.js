import { Inter } from "next/font/google";
import "./globals.css";
import AppShell from "@/components/layout/AppShell";

const inter = Inter({ subsets: ["latin"] });

export const metadata = {
  title: "SJ-DAS Professional | AI Textile Suite",
  description: "Advanced Generative Design System",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en" className="dark">
      <body className={`${inter.className} bg-background text-foreground antialiased overflow-hidden`}>
        <AppShell>
          {children}
        </AppShell>
      </body>
    </html>
  );
}
