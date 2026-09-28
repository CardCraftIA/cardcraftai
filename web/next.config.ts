import type { NextConfig } from 'next';

const nextConfig: NextConfig = {
  outputFileTracingIncludes: {'/api/catalog': ['./data/catalog_name_index_tcgdex_en.json']}
};
export default nextConfig;
