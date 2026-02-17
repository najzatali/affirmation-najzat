import "./globals.css";
import { LanguageProvider } from "../components/LanguageContext";

export const metadata = {
  title: "AIMPACT Academy",
  description: "Adaptive AI learning platform for individuals and teams",
};

export default function RootLayout({ children }) {
  return (
    <html lang="ru">
      <body>
        <LanguageProvider>{children}</LanguageProvider>
      </body>
    </html>
  );
}
