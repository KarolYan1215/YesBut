import type { Metadata } from 'next';
import type { ReactNode } from 'react';
import './globals.css';
import { I18nProvider } from '@/i18n';

export const metadata: Metadata = {
  title: 'YesBut - Multi-Agent Brainstorming',
  description: 'Multi-Agent Collaborative Brainstorming System',
};

interface RootLayoutProps {
  children: ReactNode;
}

export default function RootLayout({ children }: RootLayoutProps) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body>
        <I18nProvider>{children}</I18nProvider>
      </body>
    </html>
  );
}
