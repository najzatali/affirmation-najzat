import "./globals.css";
import { LanguageProvider } from "../components/LanguageContext";

export const metadata = {
  title: "Affirmation Studio",
  description: "Personal affirmations in text and audio with bilingual UX",
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
