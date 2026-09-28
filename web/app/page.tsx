import { CatalogSearch } from './components/catalog-search';

const base = (process.env.NEXT_PUBLIC_LEGACY_APP_URL || 'https://cardcraftai-test.streamlit.app').replace(/\/+$/, '');
const path = (query = '') => `${base}/${query}`;

export default function Home() {
  return <main>
    <header className="topbar"><a className="brand" href="/" aria-label="CardCraftAI, início"><span className="brand-mark">✦</span> CardCraft<span>AI</span></a>
      <nav aria-label="Navegação principal"><a href="#catalogo">Catálogo</a><a href={path('?arena=1')}>Arena</a><a href={path('?shop=1')}>Shop</a><a className="nav-button" href={path()}>Abrir app ↗</a></nav></header>
    <section className="hero"><div className="hero-copy"><span className="eyebrow">O UNIVERSO TCG EM SUAS MÃOS</span>
      <h1>Cada carta tem uma <em>história.</em><br/>Descubra a sua.</h1>
      <p>Explore cartas, analise suas descobertas com o Atlas, organize sua coleção e entre no mundo de Nacarim.</p>
      <div className="actions"><a className="primary" href="#catalogo">Explorar cartas <span>↗</span></a><a className="secondary" href={path()}>Conversar com Atlas</a></div>
      <div className="hero-proof"><span>✦ Catálogo com proveniência</span><span>✦ Coleção pessoal</span><span>✦ Arena Nacarim</span></div>
    </div><div className="hero-art" aria-hidden="true"><div className="orbit orbit-one"/><div className="orbit orbit-two"/>
      <div className="showcase-card"><div className="card-top">NACARIM <span>✦</span> GUARDIÕES DA LUZ</div><div className="sun">✧</div><div className="card-bottom">A jornada começa com uma carta</div></div>
    </div></section>
    <CatalogSearch />
    <section className="features" aria-label="Ferramentas"><div><span>01 · ATLAS</span><h3>Uma conversa que entende suas cartas.</h3><p>Consulte o catálogo primeiro. Quando precisar, a IA ajuda a interpretar o que você vê.</p><a href={path()}>Abrir Atlas ↗</a></div>
      <div><span>02 · SHOP</span><h3>Explore antes de escolher.</h3><p>Organize desejos e visite ofertas em marketplaces parceiros, com origem clara.</p><a href={path('?shop=1')}>Visitar Shop ↗</a></div>
      <div><span>03 · ARENA</span><h3>Entre no mundo de Nacarim.</h3><p>Conheça os guardiões, as cartas e a história criada para a comunidade.</p><a href={path('?arena=1')}>Entrar na Arena ↗</a></div></section>
    <footer><span>✦ CardCraftAI</span><p>Descubra. Colecione. Jogue.</p></footer>
  </main>;
}
