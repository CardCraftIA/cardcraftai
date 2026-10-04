'use client';
export default function ErrorPage({reset}:{reset:()=>void}){return <main className="page"><h1>Não foi possível abrir esta página.</h1><p>Seus dados não foram apagados. Tente novamente.</p><button onClick={reset}>Tentar novamente</button></main>;}
