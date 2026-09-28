import type { Metadata } from 'next';
import './style.css';

export const metadata: Metadata = {
  title: 'CardCraftAI · Descubra o universo TCG',
  description: 'Explore cartas TCG, organize sua coleção e descubra a Arena Nacarim.'
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="pt-BR"><body>{children}</body></html>;
}
