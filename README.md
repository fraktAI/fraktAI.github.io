<!DOCTYPE html>
<html lang="pl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Dawid Frączek | Narzędzia dla finansów i kontrolingu – fraktAI</title>
<meta id="meta-desc" name="description" content="Dawid Frączek – absolwent finansów i rachunkowości (specjalizacja controlling) tworzy narzędzia dla działów finansów i kontrolingu: raportowanie, weryfikacja danych, kalkulatory. Zobacz projekty i napisz do mnie.">
<meta id="og-title" property="og:title" content="Dawid Frączek | fraktAI">
<meta id="og-desc" property="og:description" content="Narzędzia dla działów finansów i kontrolingu, tworzone z pomocą AI.">
<meta property="og:type" content="website">
<meta name="theme-color" content="#0A0A0A">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 90'%3E%3Crect width='100' height='90' fill='%230A0A0A'/%3E%3Cpolygon points='50,8 20,78 80,78' fill='%23E10600'/%3E%3C/svg%3E">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
  :root{
    --bg:#0A0A0A;--panel:#121212;--panel-2:#181818;--line:#262626;
    --text:#F5F5F5;--muted:#9A9A9A;--red:#E10600;--red-soft:rgba(225,6,0,.12);
    --radius:18px;--max:1120px;
  }
  *{box-sizing:border-box;margin:0;padding:0}
  html{scroll-behavior:smooth;scroll-padding-top:80px}
  body{font-family:'Poppins','Segoe UI',system-ui,-apple-system,Arial,sans-serif;background:var(--bg);color:var(--text);line-height:1.65;-webkit-font-smoothing:antialiased;overflow-x:hidden}
  a{color:inherit;text-decoration:none}
  img,svg{display:block;max-width:100%}
  .wrap{width:100%;max-width:var(--max);margin:0 auto;padding:0 24px}
  section{padding:96px 0}
  .eyebrow{display:inline-block;font-size:.78rem;font-weight:600;letter-spacing:.18em;text-transform:uppercase;color:var(--red);margin-bottom:16px}
  h1,h2,h3{line-height:1.15;font-weight:700;letter-spacing:-.02em}
  h2{font-size:clamp(1.9rem,4vw,2.8rem);margin-bottom:18px}
  .lead{color:var(--muted);font-size:1.05rem;max-width:640px}
  .accent{color:var(--red)}
  :focus-visible{outline:2px solid #fff;outline-offset:3px;border-radius:6px}

  header{position:sticky;top:0;z-index:50;background:rgba(10,10,10,.82);backdrop-filter:blur(14px);-webkit-backdrop-filter:blur(14px);border-bottom:1px solid var(--line)}
  .nav{display:flex;align-items:center;justify-content:space-between;height:68px}
  .brand{display:flex;align-items:center;gap:12px;font-weight:700;font-size:1.25rem;letter-spacing:-.02em}
  .brand svg{width:34px;height:auto}
  .brand span b{color:var(--red);font-weight:700}
  .links{display:flex;align-items:center;gap:26px;font-size:.92rem;color:var(--muted)}
  .links a:hover{color:var(--text)}
  .btn{display:inline-flex;align-items:center;justify-content:center;gap:10px;padding:13px 26px;border-radius:999px;font-weight:600;font-size:.95rem;border:1px solid transparent;cursor:pointer;font-family:inherit;transition:transform .2s ease,background .2s ease,border-color .2s ease}
  .btn:hover{transform:translateY(-2px)}
  .btn-red{background:var(--red);color:#fff}
  .btn-red:hover{background:#ff1a0f}
  .btn-ghost{border-color:#3a3a3a;color:var(--text);background:transparent}
  .btn-ghost:hover{border-color:#fff}
  .nav .btn{padding:10px 22px;font-size:.88rem}

  .lang{display:flex;gap:2px;padding:3px;border:1px solid var(--line);border-radius:999px;background:var(--panel)}
  .lang button{background:none;border:0;color:var(--muted);cursor:pointer;font-family:inherit;font-weight:600;font-size:.76rem;letter-spacing:.06em;padding:6px 12px;border-radius:999px;transition:background .2s,color .2s}
  .lang button:hover{color:var(--text)}
  .lang button[aria-pressed="true"]{background:var(--red);color:#fff}

  .hero{padding:84px 0 96px;position:relative;overflow:hidden}
  .hero::before{content:"";position:absolute;right:-180px;top:-160px;width:640px;height:640px;background:radial-gradient(circle,rgba(225,6,0,.22),transparent 65%);pointer-events:none}
  .hero-grid{display:grid;grid-template-columns:1.2fr .8fr;gap:56px;align-items:center;position:relative}
  .hero h1{font-size:clamp(2.3rem,5.4vw,3.9rem);margin-bottom:24px}
  .hero p.lead{font-size:1.12rem;margin-bottom:36px}
  .cta-row{display:flex;flex-wrap:wrap;gap:14px}
  .hero-art{display:flex;justify-content:center}
  .hero-art svg{width:100%;max-width:400px;height:auto;filter:drop-shadow(0 30px 60px rgba(225,6,0,.18))}
  .hero-art polygon{opacity:0;animation:pop .6s ease forwards;transform-box:fill-box;transform-origin:center}
  @keyframes pop{from{opacity:0;transform:scale(.4)}to{opacity:1;transform:scale(1)}}
  .r{fill:var(--red)}.w{fill:#fff}
  .badges{display:flex;flex-wrap:wrap;gap:10px;margin-top:40px}
  .badge{padding:8px 16px;border:1px solid var(--line);border-radius:999px;font-size:.82rem;color:var(--muted);background:var(--panel)}

  .about{background:var(--panel);border-top:1px solid var(--line);border-bottom:1px solid var(--line)}
  .about-grid{display:grid;grid-template-columns:1fr 1fr;gap:64px;align-items:start}
  .about p{color:var(--muted);margin-bottom:18px}
  .about p strong{color:var(--text);font-weight:600}
  .facts{display:grid;gap:16px}
  .fact{display:flex;gap:18px;align-items:flex-start;padding:22px;border:1px solid var(--line);border-radius:var(--radius);background:var(--bg)}
  .ico{flex:0 0 46px;width:46px;height:46px;border-radius:12px;background:var(--red-soft);display:grid;place-items:center;color:var(--red)}
  .fact h3{font-size:1.05rem;margin-bottom:4px}
  .fact p{margin:0;font-size:.92rem}

  .head{margin-bottom:48px}
  .cards{display:grid;grid-template-columns:repeat(3,1fr);gap:22px}
  .card{padding:32px 28px;border:1px solid var(--line);border-radius:var(--radius);background:var(--panel);transition:transform .25s,border-color .25s;position:relative;overflow:hidden}
  .card::after{content:"";position:absolute;left:0;top:0;height:3px;width:0;background:var(--red);transition:width .35s ease}
  .card:hover{transform:translateY(-6px);border-color:#3a3a3a}
  .card:hover::after{width:100%}
  .card .ico{width:50px;height:50px;border-radius:14px;margin-bottom:22px}
  .card h3{font-size:1.15rem;margin-bottom:10px}
  .card p{color:var(--muted);font-size:.94rem}

  /* PORTFOLIO */
  .portfolio{background:var(--panel);border-top:1px solid var(--line);border-bottom:1px solid var(--line)}
  .filters{display:flex;flex-wrap:wrap;gap:10px;margin-bottom:34px}
  .filters button{font-family:inherit;font-size:.86rem;font-weight:500;padding:9px 20px;border-radius:999px;border:1px solid #333;background:transparent;color:var(--muted);cursor:pointer;transition:all .2s}
  .filters button:hover{color:var(--text);border-color:#666}
  .filters button[aria-pressed="true"]{background:var(--red);border-color:var(--red);color:#fff}
  .proj-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:24px}
  .proj{display:flex;flex-direction:column;border:1px solid var(--line);border-radius:22px;background:var(--bg);overflow:hidden;transition:transform .25s,border-color .25s}
  .proj:hover{transform:translateY(-5px);border-color:#3d3d3d}
  .proj.wide{grid-column:1/-1;flex-direction:row}
  .proj.wide .viz{flex:0 0 42%;height:auto;min-height:190px;border-bottom:0;border-right:1px solid var(--line)}
  .viz{height:190px;background:linear-gradient(160deg,#161616,#0c0c0c);border-bottom:1px solid var(--line);display:grid;place-items:center;padding:22px;position:relative;overflow:hidden}
  .viz::before{content:"";position:absolute;right:-60px;top:-60px;width:200px;height:200px;background:radial-gradient(circle,rgba(225,6,0,.16),transparent 65%)}
  .proj-body{padding:26px 28px 28px;display:flex;flex-direction:column;flex:1}
  .meta{display:flex;flex-wrap:wrap;align-items:center;gap:10px;margin-bottom:12px;min-height:26px}
  .plat{font-size:.72rem;font-weight:600;letter-spacing:.1em;text-transform:uppercase;color:var(--red)}
  .ver{font-size:.72rem;color:var(--muted);border:1px solid var(--line);padding:2px 9px;border-radius:999px}
  .proj h3{font-size:1.35rem;margin-bottom:8px}
  .proj p.d{color:var(--muted);font-size:.95rem;margin-bottom:16px}
  .proj ul{list-style:none;display:grid;gap:8px;margin-bottom:20px}
  .proj li{display:flex;gap:11px;font-size:.88rem;color:#c9c9c9;line-height:1.5}
  .proj li::before{content:"";flex:0 0 8px;height:8px;margin-top:7px;background:var(--red);clip-path:polygon(50% 0,0 100%,100% 100%)}
  .tags{display:flex;flex-wrap:wrap;gap:8px;margin-top:auto}
  .tag{font-size:.74rem;padding:4px 11px;border-radius:999px;background:var(--panel-2);border:1px solid var(--line);color:var(--muted)}
  .proj .link{margin-top:18px;font-size:.88rem;font-weight:600;color:var(--red)}
  .proj .link:hover{text-decoration:underline}

  /* mini mockups */
  .mk{width:100%;max-width:290px;font-size:.72rem;color:#ddd}
  .mk .row{display:flex;justify-content:space-between;align-items:center;gap:10px}
  .mk .bar{height:8px;border-radius:8px;background:#262626;overflow:hidden;margin:8px 0}
  .mk .bar i{display:block;height:100%;background:var(--red);border-radius:8px}
  .mk .pill{padding:2px 9px;border-radius:999px;font-weight:600;font-size:.66rem;background:rgba(255,255,255,.1);color:#fff}
  .mk .pill.red{background:var(--red)}
  .mk .box{background:#1b1b1b;border:1px solid #2a2a2a;border-radius:12px;padding:11px 13px}
  .mk .box+.box{margin-top:8px}
  .mk .muted{color:#7d7d7d}
  .ring{display:flex;align-items:center;gap:18px}
  .ring svg{width:92px;height:92px;flex:none}
  .bars{display:flex;align-items:flex-end;gap:9px;height:92px;margin-bottom:10px}
  .bars i{flex:1;background:#fff;border-radius:4px 4px 0 0;opacity:.9}
  .bars i.r{background:var(--red);opacity:1}
  .doc{display:flex;gap:14px;align-items:flex-start}
  .doc .page{flex:1;background:#fff;border-radius:6px;padding:10px;display:grid;gap:5px}
  .doc .page i{display:block;height:5px;border-radius:3px;background:#d4d4d4}
  .doc .page i.h{width:45%;background:#111;height:7px}
  .doc .page i.s{width:70%}
  .doc .page i.r{background:var(--red);width:30%}
  .doc .side{display:grid;gap:8px;align-content:start}

  /* wsparcie */
  .coffee{margin-top:36px;display:flex;align-items:center;justify-content:space-between;gap:24px;flex-wrap:wrap;padding:26px 30px;border:1px dashed #3a3a3a;border-radius:22px;background:var(--bg)}
  .coffee[hidden]{display:none}
  .coffee h3{font-size:1.15rem;margin-bottom:4px}
  .coffee p{color:var(--muted);font-size:.92rem;max-width:560px}

  /* AI */
  .ai-grid{display:grid;grid-template-columns:1fr 1fr;gap:64px;align-items:center}
  .ai ul{list-style:none;display:grid;gap:14px;margin-top:28px}
  .ai li{display:flex;gap:14px;align-items:flex-start;color:var(--muted)}
  .ai li::before{content:"";flex:0 0 10px;height:10px;margin-top:9px;background:var(--red);clip-path:polygon(50% 0,0 100%,100% 100%)}
  .ai li strong{color:var(--text);font-weight:600}
  .phone{justify-self:center;width:260px;aspect-ratio:9/18.5;border-radius:38px;border:2px solid #333;background:#050505;padding:14px;position:relative;box-shadow:0 40px 80px rgba(0,0,0,.6),0 0 0 6px #111}
  .phone::before{content:"";position:absolute;top:12px;left:50%;transform:translateX(-50%);width:80px;height:20px;border-radius:12px;background:#000;border:1px solid #1d1d1d}
  .screen{height:100%;border-radius:26px;background:linear-gradient(180deg,#141414,#0b0b0b);padding:46px 16px 16px;display:flex;flex-direction:column;gap:10px;font-size:.72rem;overflow:hidden}
  .bubble{padding:10px 13px;border-radius:16px;max-width:88%;line-height:1.45}
  .b-user{align-self:flex-end;background:var(--red);color:#fff;border-bottom-right-radius:4px}
  .b-ai{align-self:flex-start;background:#1f1f1f;color:#ddd;border-bottom-left-radius:4px}
  .typing{align-self:flex-start;display:flex;gap:5px;padding:12px 14px;background:#1f1f1f;border-radius:16px}
  .typing i{width:6px;height:6px;border-radius:50%;background:#888;animation:blink 1.2s infinite}
  .typing i:nth-child(2){animation-delay:.2s}.typing i:nth-child(3){animation-delay:.4s}
  @keyframes blink{0%,60%,100%{opacity:.25}30%{opacity:1}}
  .input{margin-top:auto;border:1px solid #2a2a2a;border-radius:999px;padding:9px 14px;color:#666}

  /* PROCESS */
  .steps{display:grid;grid-template-columns:repeat(4,1fr);gap:22px;counter-reset:s}
  .step{padding:28px 24px;border-top:2px solid var(--line)}
  .step::before{counter-increment:s;content:"0" counter(s);display:block;font-size:2.2rem;font-weight:700;color:var(--red);margin-bottom:14px;letter-spacing:-.03em}
  .step h3{font-size:1.1rem;margin-bottom:8px}
  .step p{color:var(--muted);font-size:.92rem}

  .contact{padding-top:0}
  .contact-box{border:1px solid var(--line);border-radius:28px;padding:64px;background:radial-gradient(circle at 100% 0%,rgba(225,6,0,.22),transparent 55%),var(--panel);display:grid;grid-template-columns:1fr 1fr;gap:56px;align-items:start}
  .contact-box h2{font-size:clamp(1.9rem,4vw,2.9rem)}
  .contact-info{margin-top:30px;display:grid;gap:12px;color:var(--muted);font-size:.95rem}
  .contact-info a{color:var(--text);font-weight:500;border-bottom:1px solid var(--red)}
  .contact-info a:hover{color:var(--red)}
  form{display:grid;gap:14px}
  label{font-size:.8rem;color:var(--muted);display:grid;gap:6px}
  input,textarea{width:100%;padding:14px 16px;border-radius:12px;border:1px solid #2e2e2e;background:#0b0b0b;color:var(--text);font-family:inherit;font-size:.95rem;transition:border-color .2s}
  input:focus,textarea:focus{outline:none;border-color:var(--red)}
  textarea{min-height:130px;resize:vertical}
  .note{font-size:.76rem;color:#6d6d6d}
  footer{border-top:1px solid var(--line);padding:32px 0;color:#6d6d6d;font-size:.85rem}
  .foot{display:flex;justify-content:space-between;flex-wrap:wrap;gap:12px}

  .rv{opacity:0;transform:translateY(24px);transition:opacity .7s ease,transform .7s ease}
  .rv.in{opacity:1;transform:none}

  @media (max-width:960px){
    .cards{grid-template-columns:repeat(2,1fr)}
    .steps{grid-template-columns:repeat(2,1fr)}
  }
  @media (max-width:820px){
    section{padding:72px 0}
    .links{gap:12px}
    .links a:not(.btn){display:none}
    .hero-grid,.about-grid,.ai-grid,.contact-box,.proj-grid{grid-template-columns:1fr}
    .hero-art{order:-1}
    .hero-art svg{max-width:240px}
    .contact-box{padding:36px 24px}
    .about-grid,.ai-grid{gap:40px}
    .proj.wide{flex-direction:column}
    .proj.wide .viz{flex:none;border-right:0;border-bottom:1px solid var(--line)}
  }
  @media (max-width:560px){
    .cards,.steps{grid-template-columns:1fr}
    .wrap{padding:0 18px}
    .brand{font-size:1.1rem;gap:8px}.brand svg{width:28px}
    .lang button{padding:6px 9px}
    .nav .btn{padding:9px 16px}
    .proj-body{padding:22px 20px 24px}
  }
  @media (prefers-reduced-motion:reduce){
    *{animation:none!important;transition:none!important}
    .hero-art polygon,.rv{opacity:1;transform:none}
  }
</style>
</head>
<body>

<header>
  <div class="wrap nav">
    <a class="brand" href="#top" data-i18n-aria="aria.home" aria-label="fraktAI – strona główna">
      <svg id="logo" viewBox="0 0 100 87" aria-hidden="true"></svg>
      <span>frakt<b>AI</b></span>
    </a>
    <nav class="links">
      <a href="#o-mnie" data-i18n="nav.about">O mnie</a>
      <a href="#oferta" data-i18n="nav.offer">Oferta</a>
      <a href="#projekty" data-i18n="nav.projects">Projekty</a>
      <a href="#proces" data-i18n="nav.process">Jak pracuję</a>
      <div class="lang" role="group" aria-label="Język / Language">
        <button type="button" data-lang="pl" aria-pressed="true">PL</button>
        <button type="button" data-lang="en" aria-pressed="false">EN</button>
      </div>
      <a class="btn btn-red" href="#kontakt" data-i18n="nav.contact">Kontakt</a>
    </nav>
  </div>
</header>

<main id="top">

  <section class="hero">
    <div class="wrap hero-grid">
      <div>
        <span class="eyebrow">Dawid Frączek · fraktAI</span>
        <h1 data-i18n="hero.title">Automatyzuję pracę działów <span class="accent">finansów i kontrolingu.</span></h1>
        <p class="lead" data-i18n="hero.lead">Łączę wykształcenie i praktykę w controllingu z pracą z asystentami AI. Buduję narzędzia do raportowania, weryfikacji danych i analiz, które oszczędzają czas Twojego zespołu.</p>
        <div class="cta-row">
          <a class="btn btn-red" href="#kontakt" data-i18n="hero.cta1">Napisz do mnie</a>
          <a class="btn btn-ghost" href="#projekty" data-i18n="hero.cta2">Zobacz projekty</a>
        </div>
        <div class="badges">
          <span class="badge" data-i18n="hero.b1">Controlling i raportowanie</span>
          <span class="badge" data-i18n="hero.b2">Księgowość</span>
          <span class="badge" data-i18n="hero.b3">Weryfikacja danych</span>
          <span class="badge" data-i18n="hero.b4">Tworzone z pomocą AI</span>
        </div>
      </div>
      <div class="hero-art">
        <svg id="hero-fractal" viewBox="0 0 100 87" role="img" data-i18n-aria="aria.fractal" aria-label="Fraktal – symbol fraktAI"></svg>
      </div>
    </div>
  </section>

  <section class="about" id="o-mnie">
    <div class="wrap about-grid">
      <div class="rv">
        <span class="eyebrow" data-i18n="about.eyebrow">O mnie</span>
        <h2 data-i18n="about.title">Cześć, jestem Dawid.</h2>
        <p data-i18n="about.p1">Jestem absolwentem <strong>Uniwersytetu Ekonomicznego we Wrocławiu</strong>: studia magisterskie na kierunku finanse i rachunkowość, ze specjalizacją rachunkowość zarządcza i controlling, oraz studia podyplomowe, m.in. na kierunku Dyrektor finansowy.</p>
        <p data-i18n="about.p2">Na co dzień <strong>współpracuję w kontrolingu w dużej spółce giełdowej</strong>. Znam więc raporty, zamknięcia i pliki z systemów księgowych z praktyki, a narzędzia buduję tak, by rozwiązywały konkretne problemy zespołów finansowych.</p>
        <p data-i18n="about.p3">Firma <strong>fraktAI</strong> łączy tę wiedzę z pracą z asystentami AI. „Frakt” to fraktale: prosty wzór powtarzany w różnych skalach daje złożony, a uporządkowany obraz. „AI” to sposób, w jaki pracuję. Dla użytkownika narzędzia mają być proste, a dane, gdzie się da, przetwarzane lokalnie.</p>
      </div>
      <div class="facts">
        <div class="fact rv">
          <div class="ico"><svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M2 9l10-5 10 5-10 5z"/><path d="M6 11v5c0 1.5 3 3 6 3s6-1.5 6-3v-5"/></svg></div>
          <div><h3 data-i18n="fact.1t">Uniwersytet Ekonomiczny we Wrocławiu</h3><p data-i18n="fact.1p">Magister: finanse i rachunkowość, specjalizacja rachunkowość zarządcza i controlling.</p></div>
        </div>
        <div class="fact rv">
          <div class="ico"><svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M5 4h11a3 3 0 013 3v13H8a3 3 0 01-3-3z"/><path d="M5 17a3 3 0 013-3h11"/></svg></div>
          <div><h3 data-i18n="fact.2t">Studia podyplomowe</h3><p data-i18n="fact.2p">M.in. kierunek Dyrektor finansowy.</p></div>
        </div>
        <div class="fact rv">
          <div class="ico"><svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M4 20V10M10 20V4M16 20v-7M22 20H2"/></svg></div>
          <div><h3 data-i18n="fact.3t">Praktyka w kontrolingu</h3><p data-i18n="fact.3p">Współpraca w kontrolingu w dużej spółce giełdowej.</p></div>
        </div>
      </div>
    </div>
  </section>

  <section id="oferta">
    <div class="wrap">
      <div class="head rv">
        <span class="eyebrow" data-i18n="svc.eyebrow">Oferta</span>
        <h2 data-i18n="svc.title">Co mogę dla Ciebie zbudować</h2>
        <p class="lead" data-i18n="svc.lead">Od pierwszego szkicu po działające narzędzie w rękach użytkowników.</p>
      </div>
      <div class="cards">
        <article class="card rv">
          <div class="ico"><svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M4 20V10M10 20V4M16 20v-7M22 20H2"/></svg></div>
          <h3 data-i18n="svc.1t">Raportowanie i analizy</h3>
          <p data-i18n="svc.1p">Rachunek zysków i strat, bilans, wskaźniki i zestawienia kontrahentów budowane z eksportów z systemów księgowych, z wykresami i zapisem do PDF.</p>
        </article>
        <article class="card rv">
          <div class="ico"><svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><path d="M9 12l2 2 4-4"/></svg></div>
          <h3 data-i18n="svc.2t">Weryfikacja i zgodność</h3>
          <p data-i18n="svc.2p">Weryfikacja kontrahentów i rachunków w Białej Liście VAT, obsługa plików JPK_VAT oraz faktur KSeF FA(3).</p>
        </article>
        <article class="card rv">
          <div class="ico"><svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="5" y="2" width="14" height="20" rx="2"/><path d="M8 6h8M8 11h2M14 11h2M8 15h2M14 15h2M8 19h2M14 19h2"/></svg></div>
          <h3 data-i18n="svc.3t">Kalkulatory i symulacje</h3>
          <p data-i18n="svc.3p">Modele porównujące warianty, np. koszt zatrudnienia i „na rękę” przy różnych formach współpracy, z edytowalnymi parametrami.</p>
        </article>
        <article class="card rv">
          <div class="ico"><svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><path d="M14 2v6h6M8 13h8M8 17h8"/></svg></div>
          <h3 data-i18n="svc.4t">Automatyzacja pracy z plikami</h3>
          <p data-i18n="svc.4p">Import z Excela, CSV i XML, przetwarzanie dużych zestawień i eksport do PDF i CSV zamiast ręcznego przepisywania.</p>
        </article>
        <article class="card rv">
          <div class="ico"><svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3l1.8 4.7L18.5 9.5l-4.7 1.8L12 16l-1.8-4.7L5.5 9.5l4.7-1.8z"/><path d="M19 15l.8 2.2L22 18l-2.2.8L19 21l-.8-2.2L16 18l2.2-.8z"/></svg></div>
          <h3 data-i18n="svc.5t">Szybkie prototypy i iteracje</h3>
          <p data-i18n="svc.5p">Dzięki pracy z asystentami AI szybko powstaje działający prototyp, który możesz ocenić i poprawić, zanim zainwestujesz w pełną wersję.</p>
        </article>
        <article class="card rv">
          <div class="ico"><svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="4" y="11" width="16" height="10" rx="2"/><path d="M8 11V7a4 4 0 018 0v4"/></svg></div>
          <h3 data-i18n="svc.6t">Prywatność danych</h3>
          <p data-i18n="svc.6p">Narzędzia działające w przeglądarce i lokalnie, bez wysyłania Twoich plików finansowych na obce serwery (tam, gdzie to możliwe).</p>
        </article>
      </div>
    </div>
  </section>

  <section class="portfolio" id="projekty">
    <div class="wrap">
      <div class="head rv">
        <span class="eyebrow" data-i18n="pf.eyebrow">Projekty</span>
        <h2 data-i18n="pf.title">Wybrane projekty</h2>
        <p class="lead" data-i18n="pf.lead">Narzędzia, które zbudowałem dla księgowości i kontrolingu.</p>
      </div>
      <div class="proj-grid" id="projGrid"></div>
      <div class="coffee rv" id="coffee" hidden>
        <div>
          <h3 data-i18n="cf.title">Przydało się? Postaw mi kawę.</h3>
          <p data-i18n="cf.text">Jeśli któreś z moich narzędzi oszczędziło Ci czas, możesz mnie wesprzeć symboliczną kawą. Dziękuję!</p>
        </div>
        <a class="btn btn-red" id="coffeeBtn" href="#" target="_blank" rel="noopener">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 8h12v6a5 5 0 01-5 5h-2a5 5 0 01-5-5V8z"/><path d="M17 10h1.5a2.5 2.5 0 010 5H17M8 2v2M12 2v2M16 2v2"/></svg>
          <span data-i18n="cf.btn">Postaw mi kawę</span>
        </a>
      </div>
    </div>
  </section>

  <section class="ai" id="ai">
    <div class="wrap ai-grid">
      <div class="rv">
        <span class="eyebrow" data-i18n="ai.eyebrow">Praca z AI</span>
        <h2 data-i18n="ai.title">Jak tworzę z AI</h2>
        <p class="lead" data-i18n="ai.lead">Nie piszę aplikacji sam: tworzę je razem z asystentami AI, takimi jak Claude i Codex. Mówię o tym otwarcie, bo to część mojego sposobu pracy.</p>
        <ul>
          <li><span data-i18n="ai.l1"><strong>Szybciej od pomysłu do prototypu.</strong> Asystenci pomagają mi pisać, testować i poprawiać kod.</span></li>
          <li><span data-i18n="ai.l2"><strong>Decyzje należą do mnie.</strong> Ustalam wymagania, sprawdzam wyniki i odpowiadam za efekt.</span></li>
          <li><span data-i18n="ai.l3"><strong>Uczciwie o ograniczeniach.</strong> W aplikacjach opisuję, co robią, a czego nie, żebyś wiedział, czego się spodziewać.</span></li>
          <li><span data-i18n="ai.l4"><strong>Prywatność od początku.</strong> Gdzie się da, dane zostają u Ciebie, w przeglądarce lub na urządzeniu.</span></li>
        </ul>
      </div>
      <div class="phone rv" aria-hidden="true">
        <div class="screen">
          <div class="bubble b-user" data-i18n="chat.1">Dodaj do kalkulatora tryb ciemny i wydruk.</div>
          <div class="bubble b-ai" data-i18n="chat.2">Gotowe. Dodałem przełącznik stylu i widok do druku A4.</div>
          <div class="bubble b-user" data-i18n="chat.3">Sprawdź jeszcze widok na telefonie.</div>
          <div class="typing"><i></i><i></i><i></i></div>
          <div class="input" data-i18n="chat.input">Napisz wiadomość…</div>
        </div>
      </div>
    </div>
  </section>

  <section id="proces" style="padding-top:0">
    <div class="wrap">
      <div class="head rv">
        <span class="eyebrow" data-i18n="proc.eyebrow">Jak pracuję</span>
        <h2 data-i18n="proc.title">Prosty proces, przewidywalny efekt</h2>
        <p class="lead" data-i18n="proc.lead">Wiesz, na jakim etapie jesteśmy i co dzieje się dalej.</p>
      </div>
      <div class="steps">
        <div class="step rv"><h3 data-i18n="proc.1t">Rozmowa</h3><p data-i18n="proc.1p">Poznaję Twój proces, raporty i dane. Ustalamy zakres i kierunek.</p></div>
        <div class="step rv"><h3 data-i18n="proc.2t">Projekt</h3><p data-i18n="proc.2p">Przygotowuję makiety i plan funkcji, żebyś zobaczył narzędzie, zanim powstanie.</p></div>
        <div class="step rv"><h3 data-i18n="proc.3t">Budowa</h3><p data-i18n="proc.3p">Tworzę aplikację etapami, z regularnymi podglądami i możliwością zgłaszania uwag.</p></div>
        <div class="step rv"><h3 data-i18n="proc.4t">Wdrożenie i rozwój</h3><p data-i18n="proc.4p">Przekazuję gotowe rozwiązanie, a potem rozwijam je na podstawie Twoich potrzeb.</p></div>
      </div>
    </div>
  </section>

  <section class="contact" id="kontakt">
    <div class="wrap">
      <div class="contact-box rv">
        <div>
          <span class="eyebrow" data-i18n="ct.eyebrow">Kontakt</span>
          <h2 data-i18n="ct.title">Masz proces do zautomatyzowania? <span class="accent">Porozmawiajmy.</span></h2>
          <p class="lead" data-i18n="ct.lead">Opisz w kilku zdaniach, czego potrzebujesz. Odpowiem i zaproponuję, jak możemy to zrealizować.</p>
          <div class="contact-info">
            <span>E-mail: <a id="mailLink" href="#"></a></span>
            <span>Dawid Frączek · fraktAI</span>
          </div>
        </div>
        <form id="form">
          <label><span data-i18n="ct.name">Imię</span>
            <input type="text" id="f-name" data-i18n-ph="ct.nameph" placeholder="Jak mam się do Ciebie zwracać?" required>
          </label>
          <label>E-mail
            <input type="email" id="f-mail" data-i18n-ph="ct.mailph" placeholder="twoj@adres.pl" required>
          </label>
          <label><span data-i18n="ct.msg">Twój pomysł</span>
            <textarea id="f-msg" data-i18n-ph="ct.msgph" placeholder="Jaki raport lub proces chcesz usprawnić?" required></textarea>
          </label>
          <button class="btn btn-red" type="submit" data-i18n="ct.send">Wyślij wiadomość</button>
          <p class="note" data-i18n="ct.note">Formularz otworzy Twój program pocztowy z gotową wiadomością.</p>
        </form>
      </div>
    </div>
  </section>

</main>

<footer>
  <div class="wrap foot">
    <span>© 2026 fraktAI · Dawid Frączek</span>
    <span data-i18n="foot.tag">Narzędzia dla finansów i kontrolingu</span>
  </div>
</footer>

<script>
  /* >>> USTAWIENIA: wpisz swój e-mail (jedno miejsce w pliku) <<< */
  var EMAIL = 'twoj@email.pl';
  /* Link do wpłat "Postaw mi kawę" (Buy Me a Coffee, Ko-fi, buycoffee.to, Stripe Payment Link itp.).
     Puste = blok z przyciskiem jest ukryty. */
  var COFFEE_URL = '';

  /* Fraktal (trójkąt Sierpińskiego) */
  (function(){
    var NS='http://www.w3.org/2000/svg',H=Math.sqrt(3)/2;
    function build(x,y,s,d,out){if(d===0){out.push([x,y,s]);return}var s2=s/2,h2=s2*H;build(x,y,s2,d-1,out);build(x-s2/2,y+h2,s2,d-1,out);build(x+s2/2,y+h2,s2,d-1,out)}
    function draw(svg,depth,animate){
      var out=[];build(50,0,100,depth,out);
      out.forEach(function(t){
        var x=t[0],y=t[1],s=t[2],hh=s*H,p=document.createElementNS(NS,'polygon');
        p.setAttribute('points',x+','+y+' '+(x-s/2)+','+(y+hh)+' '+(x+s/2)+','+(y+hh));
        var rel=y/(100*H);p.setAttribute('class',rel<0.34?'r':'w');
        if(animate)p.style.animationDelay=(rel*0.9+Math.random()*0.25).toFixed(2)+'s';
        svg.appendChild(p);
      });
    }
    draw(document.getElementById('logo'),3,false);
    draw(document.getElementById('hero-fractal'),4,true);
  })();

  /* Dane projektów (PL / EN). Pole url: wpisz adres, a pojawi się przycisk "Zobacz". */
  var PROJECTS = [
    { id:'ksef', cat:'fin', url:'', ver:'v0.9.5',
      pl:{ plat:'Web · przeglądarka', name:'Wizualizator KSeF FA(3)',
        d:'Wizualizacja i pobieranie faktur XML w standardzie KSeF FA(3) jako czytelnych dokumentów PDF.',
        b:['Przeciągnij i upuść wiele plików XML naraz','Filtry, własne notatki do faktur i konfiguracja wydruku','Pobieranie pojedynczego PDF-a albo wszystkiego jako archiwum ZIP'],
        t:['KSeF','FA(3)','XML → PDF'] },
      en:{ plat:'Web · browser', name:'KSeF FA(3) Invoice Viewer',
        d:'Turns XML invoices in the KSeF FA(3) standard into readable documents you can download as PDF.',
        b:['Drag and drop many XML files at once','Filters, your own notes on invoices and print configuration','Download a single PDF or everything as a ZIP archive'],
        t:['KSeF','FA(3)','XML → PDF'] } },
    { id:'fortnox', cat:'fin', url:'', ver:'',
      pl:{ plat:'Web · działa offline', name:'Fortnox → RZiS i Bilans',
        d:'Z eksportu księgi głównej Fortnox (Huvudbok) buduje rachunek zysków i strat, bilans oraz analizę kontrahentów.',
        b:['RZiS w układzie rodzajowym lub kalkulacyjnym, bilans, wskaźniki i wykresy','Wybór okresu (kwartały, półrocza), szczegóły kont i faktur, zapis do PDF','Plik jest przetwarzany wyłącznie w przeglądarce, bez wysyłania danych'],
        t:['Fortnox','Plan kont BAS','SEK','Excel / CSV'] },
      en:{ plat:'Web · works offline', name:'Fortnox → P&L and Balance Sheet',
        d:'Builds an income statement, balance sheet and counterparty analysis from a Fortnox general ledger (Huvudbok) export.',
        b:['Income statement by nature or by function, balance sheet, ratios and charts','Period selection (quarters, half-years), account and invoice details, PDF export','The file is processed only in your browser, no data is sent anywhere'],
        t:['Fortnox','BAS chart of accounts','SEK','Excel / CSV'] } },
    { id:'vat', cat:'fin', url:'', ver:'v1.6',
      pl:{ plat:'Web · przeglądarka', name:'Biała Lista VAT – Weryfikator',
        d:'Weryfikuje rachunki bankowe i numery NIP w Rejestrze Podatników VAT (Biała Lista), także dla całych plików Excel i JPK_VAT.',
        b:['Dane z API Ministerstwa Finansów: status VAT, nazwa, REGON, adres, rachunki','Do 30 rachunków naraz, import .xlsx / .csv oraz JPK_V7M z dostawcami','Eksport wyników do CSV, pamięć podręczna odpowiedzi, tryb ciemny'],
        t:['API MF','JPK_VAT','NIP','Excel / CSV'] },
      en:{ plat:'Web · browser', name:'VAT White List Verifier',
        d:'Checks bank accounts and tax IDs (NIP) against the Polish VAT taxpayer register (White List), including whole Excel and JPK_VAT files.',
        b:['Data from the Ministry of Finance API: VAT status, name, REGON, address, accounts','Up to 30 accounts at once, .xlsx / .csv import and JPK_V7M with suppliers','CSV export, response caching and a dark mode'],
        t:['MF API','JPK_VAT','NIP','Excel / CSV'] } },
    { id:'kalk', cat:'fin', url:'', ver:'',
      pl:{ plat:'Web · działa offline', name:'Kalkulator zmiany formy współpracy',
        d:'Porównuje „na rękę” i koszt pracodawcy dziś oraz po zmianie formy współpracy lub wynagrodzenia: umowa o pracę, zlecenie, B2B, kontrakt menadżerski.',
        b:['Do sześciu współprac po każdej stronie, z ZUS, PIT, PPK i opodatkowaniem B2B (skala, liniowy, ryczałt)','Wylicza kwotę potrzebną, by zachować obecne „na rękę”','Edytowalne stawki na 2026 rok, wydruk i tryb ciemny, dane zostają w przeglądarce'],
        t:['ZUS','PIT','B2B','PPK'] },
      en:{ plat:'Web · works offline', name:'Employment Type Change Calculator',
        d:'Compares take-home pay and employer cost today and after changing the form of cooperation or pay: employment contract, mandate contract, B2B, managerial contract.',
        b:['Up to six engagements per side, with social security, income tax, PPK and B2B taxation (scale, flat, lump-sum)','Works out the amount needed to keep the current take-home pay','Editable 2026 rates, printing and a dark mode, data stays in your browser'],
        t:['Social security','Income tax','B2B','PPK'] } },

  ];

  /* Miniaturki (proste makiety, bez tekstów do tłumaczenia) */
  var VIZ = {
    ksef:'<div class="mk"><div class="doc"><div class="page"><i class="h"></i><i class="s"></i><i></i><i></i><i class="s"></i><i></i><i class="r"></i></div><div class="side"><span class="pill red">FA(3)</span><span class="pill">XML</span><span class="pill">PDF</span><span class="pill">ZIP</span></div></div></div>',
    fortnox:'<div class="mk"><div class="bars"><i style="height:40%"></i><i style="height:62%"></i><i class="r" style="height:88%"></i><i style="height:55%"></i><i style="height:72%"></i><i class="r" style="height:96%"></i></div><div class="row"><span class="pill red">RZiS</span><span class="pill">Bilans</span><span class="muted">SEK</span></div></div>',
    vat:'<div class="mk"><div class="box"><div class="row"><span>NIP ••• ••• 78 90</span><span class="pill">✓</span></div></div><div class="box"><div class="row"><span>PL •• •••• •••• 4412</span><span class="pill">✓</span></div></div><div class="box"><div class="row"><span>NIP ••• ••• 31 05</span><span class="pill red">✕</span></div></div></div>',
    kalk:'<div class="mk"><div class="row" style="gap:10px"><div class="box" style="flex:1"><div class="muted">UoP</div><b>7 420</b><div class="bar"><i style="width:62%"></i></div></div><span style="color:#E10600;font-weight:700;font-size:1.1rem">→</span><div class="box" style="flex:1"><div class="muted">B2B</div><b>8 310</b><div class="bar"><i style="width:75%"></i></div></div></div><div class="row" style="margin-top:12px;justify-content:flex-start;gap:8px"><span class="pill red">+ 890</span><span class="pill">ZUS</span><span class="pill">PIT</span><span class="muted">PLN</span></div></div>',
  };

  var EN = {
    'nav.about':'About','nav.offer':'Services','nav.projects':'Projects','nav.process':'How I work','nav.contact':'Contact',
    'aria.home':'fraktAI – home','aria.fractal':'Fractal – the fraktAI symbol',
    'hero.title':'I automate the work of <span class="accent">finance and controlling teams.</span>',
    'hero.lead':'I combine my education and practice in controlling with working alongside AI assistants. I build tools for reporting, data verification and analysis that save your team time.',
    'hero.cta1':'Get in touch','hero.cta2':'See projects','hero.b1':'Controlling and reporting','hero.b4':'Built with AI',
    'about.eyebrow':'About me','about.title':'Hi, I\'m Dawid.',
    'about.p1':'I am a graduate of the <strong>Wrocław University of Economics</strong>: a master\'s degree in finance and accounting, specializing in management accounting and controlling, plus postgraduate studies, including a Chief Financial Officer programme.',
    'about.p2':'Day to day I <strong>work in controlling at a large listed company</strong>. So I know reports, closings and files from accounting systems from practice, and I build tools to solve the real problems of finance teams.',
    'about.p3':'<strong>fraktAI</strong> combines that knowledge with working alongside AI assistants. “Frakt” stands for fractals: a simple pattern repeated at different scales gives a complex yet orderly picture. “AI” is how I work. For the user the tools are meant to be simple, and data is processed locally wherever possible.',
    'fact.1t':'Wrocław University of Economics','fact.1p':'Master\'s: finance and accounting, specialization in management accounting and controlling.',
    'fact.2t':'Postgraduate studies','fact.2p':'Including the Chief Financial Officer programme.',
    'fact.3t':'Controlling practice','fact.3p':'Working in controlling at a large listed company.',
    'svc.eyebrow':'Services','svc.title':'What I can build for you','svc.lead':'From the first sketch to a working tool in your users\' hands.',
    'svc.1t':'Reporting and analysis','svc.1p':'Income statements, balance sheets, ratios and counterparty summaries built from accounting-system exports, with charts and PDF export.',
    'svc.2t':'Verification and compliance','svc.2p':'Verifying counterparties and bank accounts against the VAT White List, handling JPK_VAT files and KSeF FA(3) invoices.',
    'svc.3t':'Calculators and simulations','svc.3p':'Models that compare scenarios, e.g. employment cost and take-home pay under different forms of cooperation, with editable parameters.',
    'svc.4t':'File-handling automation','svc.4p':'Import from Excel, CSV and XML, processing of large datasets and export to PDF and CSV instead of manual re-typing.',
    'svc.5t':'Fast prototypes and iterations','svc.5p':'Working with AI assistants, I can get a working prototype in front of you early, so you can react to it before investing in the full version.',
    'svc.6t':'Data privacy','svc.6p':'Tools that run in the browser and locally, without sending your financial files to foreign servers (where possible).',
    'pf.eyebrow':'Projects','pf.title':'Selected projects','pf.lead':'Tools I have built for accounting and controlling.',
    'pf.all':'All','pf.fin':'Finance and accounting','pf.mobile':'Mobile apps','pf.filter':'Project filter','pf.view':'View project',
    'ai.eyebrow':'Working with AI','ai.title':'How I build with AI',
    'ai.lead':'I do not write the apps alone: I build them together with AI assistants such as Claude and Codex. I say so openly, because it is part of how I work.',
    'ai.l1':'<strong>Faster from idea to prototype.</strong> Assistants help me write, test and improve code.',
    'ai.l2':'<strong>I make the decisions.</strong> I set the requirements, review the results and take responsibility for the outcome.',
    'ai.l3':'<strong>Honest about limits.</strong> In my apps I describe what they do and what they do not, so you know what to expect.',
    'ai.l4':'<strong>Privacy from the start.</strong> Where possible, data stays with you, in your browser or on your device.',
    'chat.1':'Add dark mode and printing to the calculator.','chat.2':'Done. I added a style switch and an A4 print view.','chat.3':'Check the phone view too.','chat.input':'Type a message…',
    'proc.eyebrow':'How I work','proc.title':'A simple process, a predictable result','proc.lead':'You always know where we are and what comes next.',
    'proc.1t':'Conversation','proc.1p':'I learn about your process, reports and data. We agree on the scope and direction.',
    'proc.2t':'Design','proc.2p':'I prepare mockups and a feature plan so you can see the tool before it is built.',
    'proc.3t':'Build','proc.3p':'I build the app in stages, with regular previews and room for your feedback.',
    'proc.4t':'Rollout and growth','proc.4p':'I hand over the finished solution, then keep improving it based on your needs.',
    'ct.eyebrow':'Contact','ct.title':'Got a process to automate? <span class="accent">Let\'s talk.</span>',
    'ct.lead':'Describe in a few sentences what you need. I will reply and suggest how we can make it happen.',
    'ct.name':'Name','ct.nameph':'How should I address you?','ct.mailph':'you@example.com','ct.msg':'Your idea','ct.msgph':'Which report or process do you want to improve?',
    'ct.send':'Send message','ct.note':'The form will open your email app with a ready message.',
    'cf.title':'Was it useful? Buy me a coffee.',
    'cf.text':'If one of my tools saved you time, you can support me with a small coffee. Thank you!',
    'cf.btn':'Buy me a coffee',
    'hero.b2':'Accounting','hero.b3':'Data verification',
    'foot.tag':'Tools for finance and controlling',
    'meta.title':'Dawid Frączek | Tools for finance and controlling – fraktAI',
    'meta.desc':'Dawid Frączek – a finance and accounting graduate (controlling specialization) building tools for finance and controlling teams: reporting, data verification, calculators. See my projects and get in touch.',
    'meta.ogdesc':'Tools for finance and controlling teams, built with AI.',
    'mail.subject':'App inquiry – '
  };

  (function(){
    var current='pl', filter='all';
    var PLDESC=document.getElementById('meta-desc').getAttribute('content');
    var PLOG=document.getElementById('og-title').getAttribute('content');
    var PLOGD=document.getElementById('og-desc').getAttribute('content');
    var PLTITLE=document.title;

    var io=null;
    if('IntersectionObserver' in window){
      io=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){e.target.classList.add('in');io.unobserve(e.target)}})},{threshold:.12});
    }
    function watch(el){ if(io)io.observe(el); else el.classList.add('in'); }
    document.querySelectorAll('.rv').forEach(watch);

    function esc(s){return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;')}
    function renderProjects(){
      var L=current, grid=document.getElementById('projGrid');
      var fin=PROJECTS.filter(function(p){return p.cat==='fin'});
      function link(p){return p.url?'<a class="link" href="'+p.url+'" target="_blank" rel="noopener">'+(L==='en'?EN['pf.view']:'Zobacz projekt')+' →</a>':''}
      function tags(t){return '<div class="tags">'+t.t.map(function(x){return '<span class="tag">'+esc(x)+'</span>'}).join('')+'</div>'}
      grid.innerHTML=fin.map(function(p,i){
        var t=p[L], wide=(fin.length%2===1&&i===fin.length-1)?' wide':'';
        return '<article class="proj rv'+wide+'"><div class="viz" aria-hidden="true">'+VIZ[p.id]+'</div>'+
          '<div class="proj-body"><div class="meta"><span class="plat">'+esc(t.plat)+'</span>'+(p.ver?'<span class="ver">'+p.ver+'</span>':'')+'</div>'+
          '<h3>'+esc(t.name)+'</h3><p class="d">'+esc(t.d)+'</p>'+
          '<ul>'+t.b.map(function(x){return '<li>'+esc(x)+'</li>'}).join('')+'</ul>'+tags(t)+link(p)+'</div></article>';
      }).join('');
      grid.querySelectorAll('.rv').forEach(function(el){el.classList.add('in')});
    }

    function apply(lang){
      current=lang;var en=lang==='en';
      document.querySelectorAll('[data-i18n]').forEach(function(el){
        if(el.dataset.pl===undefined)el.dataset.pl=el.innerHTML;
        var k=el.getAttribute('data-i18n');
        el.innerHTML=(en&&EN[k]!==undefined)?EN[k]:el.dataset.pl;
      });
      document.querySelectorAll('[data-i18n-ph]').forEach(function(el){
        if(el.dataset.plPh===undefined)el.dataset.plPh=el.getAttribute('placeholder');
        var k=el.getAttribute('data-i18n-ph');
        el.setAttribute('placeholder',(en&&EN[k]!==undefined)?EN[k]:el.dataset.plPh);
      });
      document.querySelectorAll('[data-i18n-aria]').forEach(function(el){
        if(el.dataset.plAria===undefined)el.dataset.plAria=el.getAttribute('aria-label');
        var k=el.getAttribute('data-i18n-aria');
        el.setAttribute('aria-label',(en&&EN[k]!==undefined)?EN[k]:el.dataset.plAria);
      });
      document.documentElement.lang=lang;
      document.title=en?EN['meta.title']:PLTITLE;
      document.getElementById('meta-desc').setAttribute('content',en?EN['meta.desc']:PLDESC);
      document.getElementById('og-title').setAttribute('content',en?EN['meta.title']:PLOG);
      document.getElementById('og-desc').setAttribute('content',en?EN['meta.ogdesc']:PLOGD);
      document.querySelectorAll('.lang button').forEach(function(b){b.setAttribute('aria-pressed',b.getAttribute('data-lang')===lang?'true':'false')});
      renderProjects();
    }

    function saved(){try{return localStorage.getItem('fraktai-lang')}catch(e){return null}}
    function save(l){try{localStorage.setItem('fraktai-lang',l)}catch(e){}}
    document.querySelectorAll('.lang button').forEach(function(b){
      b.addEventListener('click',function(){var l=b.getAttribute('data-lang');apply(l);save(l)});
    });

    var ml=document.getElementById('mailLink');ml.textContent=EMAIL;ml.href='mailto:'+EMAIL;
    if(COFFEE_URL){document.getElementById('coffeeBtn').href=COFFEE_URL;document.getElementById('coffee').hidden=false}

    var start=saved();
    if(start!=='pl'&&start!=='en'){start=((navigator.language||'pl').toLowerCase().indexOf('pl')===0)?'pl':'en'}
    if(start==='en')apply('en');else renderProjects();

    document.getElementById('form').addEventListener('submit',function(ev){
      ev.preventDefault();
      var name=document.getElementById('f-name').value.trim(),
          mail=document.getElementById('f-mail').value.trim(),
          msg=document.getElementById('f-msg').value.trim();
      var prefix=current==='en'?EN['mail.subject']:'Zapytanie o aplikację – ';
      window.location.href='mailto:'+EMAIL+'?subject='+encodeURIComponent(prefix+name)+'&body='+encodeURIComponent(msg+'\n\n—\n'+name+'\n'+mail);
    });
  })();
</script>
</body>
</html>
