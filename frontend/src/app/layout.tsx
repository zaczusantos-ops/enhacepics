import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "ChurchPhoto Pro | Pós-Processamento Fotográfico para Cultos",
  description: "Pipeline profissional de colorimetria, restauração de tons de pele e mitigação de LEDs de palco para eventos de igreja.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="pt-BR" className="dark">
      <body className="bg-church-950 text-slate-100 antialiased font-sans min-h-screen">
        {children}
      </body>
    </html>
  );
}
