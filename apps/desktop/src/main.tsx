import React from 'react';
import { createRoot } from 'react-dom/client';
import './style.css';

function App() {
  const [bridge, setBridge] = React.useState(false);
  React.useEffect(() => { setBridge('__TAURI_INTERNALS__' in window); }, []);
  return <main>
    <header><div className="brand">GUIHGUIH <b>CYBER</b></div><div className="pill"><i /> {bridge ? 'Bridge desktop disponível' : 'Scanner indisponível nesta prévia web'}</div></header>
    <section className="hero"><div><small>PAINEL DE SEGURANÇA · MARCO 1</small><h1>Proteção local<br/>com estado real.</h1><p>Scanner manual com SHA-256, regras explicáveis e histórico local. Sem monitoramento em tempo real ou bloqueio pré-execução.</p><button disabled={!bridge} title="O scanner será habilitado quando o bridge Rust estiver integrado">Iniciar varredura</button></div><aside><small>ESTADO DO SISTEMA</small><h2>{bridge ? 'Bridge detectado' : 'Scanner não conectado'}</h2><p>Esta interface não executa um scan por conta própria.</p><hr/><span>Microsoft Defender</span><strong>Preservado · sem alterações</strong></aside></section>
    <section className="stats"><article><small>ÚLTIMA VARREDURA</small><b>—</b><span>Nenhuma sessão nesta interface</span></article><article><small>ARQUIVOS ANALISADOS</small><b>—</b><span>Scanner Python executável disponível</span></article><article><small>HISTÓRICO SQLITE</small><b>Local</b><span>Persistência no app de desktop Python</span></article></section>
    <section className="results"><div><h2>Atividade recente</h2><small>Resultados do scanner serão exibidos aqui após integração do bridge.</small></div><div className="empty">Nenhum resultado conectado</div></section>
    <footer>M1 · regras heurísticas não provam segurança · sem upload · nenhuma ação destrutiva</footer>
  </main>;
}

createRoot(document.getElementById('root')!).render(<App/>);

