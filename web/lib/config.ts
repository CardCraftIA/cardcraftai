// Public configuration is scoped by Vercel environment. Never use production defaults.
export function supabaseConfig() {
  const url = process.env.NEXT_PUBLIC_SUPABASE_URL || '';
  const key = process.env.NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY || '';
  return {url, key, configured: Boolean(url && key)};
}
export const LEGAL_VERSION = '2026-09-17';
