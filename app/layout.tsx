import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'DevExcuse Generator',
  description: 'Generate highly technical, AI-powered excuses for broken code.',
  openGraph: {
    title: 'DevExcuse Generator',
    description: 'Generate highly technical, AI-powered excuses for broken code.',
    url: 'https://devexcuse-generator.vercel.app',
    siteName: 'DevExcuse Generator',
    images: [
      {
        url: 'https://devexcuse-generator.vercel.app/og-image.png',
        width: 1200,
        height: 630,
      },
    ],
    locale: 'en_US',
    type: 'website',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'DevExcuse Generator',
    description: 'Generate highly technical excuses for broken code.',
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="bg-gray-50 text-gray-900 antialiased">
        {children}
      </body>
    </html>
  );
}