<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>MGP Fantasy League</title>
<link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Sans:wght@300;400;500;600&family=DM+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
  :root {
    --navy:#0a1628;--navy-light:#162440;--navy-card:#111d33;
    --gold:#c8a45a;--gold-light:#e2c07a;--gold-dim:#7a6235;
    --white:#f0eeea;--muted:#6b7a99;--green:#3ddc84;
    --border:rgba(200,164,90,0.15);--border-hi:rgba(200,164,90,0.4);
  }
  *{margin:0;padding:0;box-sizing:border-box;}
  body{background:var(--navy);color:var(--white);font-family:'DM Sans',sans-serif;min-height:100vh;overflow-x:hidden;}
  body::before{content:'';position:fixed;inset:0;background:radial-gradient(ellipse 80% 50% at 50% -10%,rgba(200,164,90,0.07) 0%,transparent 70%);pointer-events:none;z-index:0;}
  .grain{position:fixed;inset:0;opacity:0.025;background-image:url("data:image/svg+xml,%3Csvg viewBox='0 0 512 512' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E");pointer-events:none;z-index:0;}

  header{position:relative;z-index:10;padding:0 20px;border-bottom:1px solid var(--border);background:rgba(10,22,40,0.92);backdrop-filter:blur(12px);}
  .header-inner{max-width:680px;margin:0 auto;display:flex;align-items:center;justify-content:space-between;padding:14px 0;}
  .logo-block{display:flex;align-items:center;gap:10px;}
  .logo-badge{width:38px;height:38px;background:linear-gradient(135deg,var(--gold),#a07838);border-radius:8px;display:flex;align-items:center;justify-content:center;font-family:'Bebas Neue',sans-serif;font-size:18px;color:var(--navy);}
  .logo-text{display:flex;flex-direction:column;line-height:1;}
  .logo-main{font-family:'Bebas Neue',sans-serif;font-size:20px;color:var(--gold);letter-spacing:1.5px;}
  .logo-sub{font-size:9px;color:var(--muted);letter-spacing:2px;text-transform:uppercase;margin-top:2px;}
  .gw-pill{background:var(--navy-light);border:1px solid var(--border-hi);border-radius:20px;padding:5px 12px;display:flex;align-items:center;gap:6px;}
  .gw-pill .label{font-size:10px;color:var(--muted);text-transform:uppercase;letter-spacing:1.5px;}
  .gw-pill .num{font-family:'Bebas Neue',sans-serif;font-size:18px;color:var(--gold);line-height:1;}

  nav{position:relative;z-index:10;padding:0 20px;border-bottom:1px solid var(--border);background:rgba(10,22,40,0.7);}
  .nav-inner{max-width:680px;margin:0 auto;display:flex;}
  .nav-item{padding:10px 14px;font-size:12px;letter-spacing:1.2px;text-transform:uppercase;color:var(--muted);cursor:pointer;border-bottom:2px solid transparent;font-weight:500;transition:color .2s,border-color .2s;}
  .nav-item.active{color:var(--gold);border-bottom-color:var(--gold);}

  main{position:relative;z-index:5;max-width:680px;margin:0 auto;padding:20px 16px 100px;}
  .status-bar{display:flex;align-items:center;justify-content:space-between;margin-bottom:20px;flex-wrap:wrap;gap:8px;}
  .section-title{font-family:'Bebas Neue',sans-serif;font-size:22px;letter-spacing:2px;}
  .bonus-badge{display:flex;align-items:center;gap:6px;padding:5px 10px;border-radius:6px;font-size:11px;font-weight:500;}
  .badge-confirmed{background:rgba(61,220,132,.12);border:1px solid rgba(61,220,132,.3);color:var(--green);}
  .badge-pending{background:rgba(200,164,90,.1);border:1px solid rgba(200,164,90,.25);color:var(--gold);}
  .badge-checking{background:rgba(107,122,153,.1);border:1px solid rgba(107,122,153,.2);color:var(--muted);}
  .pulse-dot{width:7px;height:7px;border-radius:50%;background:currentColor;animation:pulse 2s ease-in-out infinite;}
  @keyframes pulse{0%,100%{opacity:1}50%{opacity:.4}}

  .loading-state{display:flex;flex-direction:column;align-items:center;padding:60px 20px;gap:14px;color:var(--muted);}
  .spinner{width:34px;height:34px;border:2px solid var(--border);border-top-color:var(--gold);border-radius:50%;animation:spin .8s linear infinite;}
  @keyframes spin{to{transform:rotate(360deg)}}
  .loading-text{font-size:13px;letter-spacing:.3px;}

  .error-state{padding:20px;background:rgba(220,80,60,.08);border:1px solid rgba(220,80,60,.2);border-radius:10px;color:#e07060;font-size:13px;line-height:1.6;}
  .error-state code{font-size:11px;opacity:.7;display:block;margin-top:8px;font-family:'DM Mono',monospace;}

  .matchups-grid{display:flex;flex-direction:column;gap:12px;}
  .matchup-card{background:var(--navy-card);border:1px solid var(--border);border-radius:12px;overflow:hidden;cursor:pointer;transition:border-color .25s,transform .15s,box-shadow .25s;animation:cardIn .35s ease both;}
  .matchup-card:nth-child(1){animation-delay:.05s}.matchup-card:nth-child(2){animation-delay:.1s}.matchup-card:nth-child(3){animation-delay:.15s}.matchup-card:nth-child(4){animation-delay:.2s}
  @keyframes cardIn{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:translateY(0)}}
  .matchup-card:active{transform:scale(.985);}
  .matchup-card:hover{border-color:var(--border-hi);box-shadow:0 4px 24px rgba(200,164,90,.08);}

  .card-top{padding:10px 16px;display:flex;align-items:center;gap:8px;border-bottom:1px solid var(--border);}
  .match-label{font-size:10px;text-transform:uppercase;letter-spacing:1.5px;color:var(--muted);font-weight:500;}
  .live-chip{margin-left:auto;background:rgba(61,220,132,.12);border:1px solid rgba(61,220,132,.25);color:var(--green);font-size:9px;padding:2px 7px;border-radius:4px;letter-spacing:1px;text-transform:uppercase;font-weight:600;display:flex;align-items:center;gap:4px;}
  .live-chip .dot{width:5px;height:5px;border-radius:50%;background:var(--green);animation:pulse 1.5s ease-in-out infinite;}
  .fin-chip{margin-left:auto;background:rgba(107,122,153,.15);border:1px solid rgba(107,122,153,.2);color:var(--muted);font-size:9px;padding:2px 7px;border-radius:4px;letter-spacing:1px;text-transform:uppercase;font-weight:600;}

  .card-body{padding:14px 16px;display:grid;grid-template-columns:1fr auto 1fr;align-items:center;gap:10px;}
  .team-side{display:flex;flex-direction:column;gap:3px;}
  .team-side.right{align-items:flex-end;text-align:right;}
  .team-name{font-size:13px;font-weight:600;color:var(--white);line-height:1.25;}
  .gk-detail{font-size:10px;color:var(--gold-dim);font-family:'DM Mono',monospace;}
  .player-count{font-size:10px;color:var(--muted);font-family:'DM Mono',monospace;}

  .score-block{display:flex;align-items:center;gap:6px;flex-shrink:0;}
  .score{font-family:'Bebas Neue',sans-serif;font-size:38px;line-height:1;min-width:42px;text-align:center;transition:color .3s;}
  .score.winning{color:var(--gold-light);}
  .score.losing{color:var(--muted);}
  .score.drawing{color:var(--white);}
  .score-sep{font-family:'Bebas Neue',sans-serif;font-size:24px;color:var(--border-hi);line-height:1;}

  .card-footer{padding:8px 16px;background:rgba(255,255,255,.02);border-top:1px solid var(--border);display:flex;align-items:center;justify-content:space-between;}
  .footer-hint{font-size:10px;color:var(--muted);}
  .footer-arrow{font-size:14px;color:var(--gold-dim);}

  .meta-row{margin-top:18px;display:flex;flex-direction:column;gap:6px;align-items:center;}
  .refresh-bar{display:flex;align-items:center;gap:7px;color:var(--muted);font-size:11px;}
  .refresh-icon{display:inline-block;}
  .refresh-icon.spinning{animation:spin .9s linear infinite;}
  .last-updated{font-size:10px;color:var(--muted);opacity:.55;font-family:'DM Mono',monospace;}
  .api-note{padding:8px 14px;background:rgba(200,164,90,.05);border:1px solid var(--border);border-radius:8px;font-size:11px;color:var(--muted);text-align:center;line-height:1.5;}
  .api-note span{color:var(--gold);}

  .bottom-nav{position:fixed;bottom:0;left:0;right:0;z-index:20;background:rgba(10,22,40,.96);backdrop-filter:blur(16px);border-top:1px solid var(--border);display:flex;justify-content:space-around;padding:8px 0 env(safe-area-inset-bottom,8px);}
  .bn-item{display:flex;flex-direction:column;align-items:center;gap:3px;padding:4px 16px;cursor:pointer;color:var(--muted);transition:color .2s;}
  .bn-item.active{color:var(--gold);}
  .bn-icon{font-size:20px;line-height:1;}
  .bn-label{font-size:9px;text-transform:uppercase;letter-spacing:1px;font-weight:600;}
</style>
</head>
<body>
<div class="grain"></div>
<header>
  <div class="header-inner">
    <div class="logo-block">
      <div class="logo-badge">MGP</div>
      <div class="logo-text">
        <span class="logo-main">MGP Fantasy</span>
        <span class="logo-sub">Morten Gamst Pedersen League</span>
      </div>
    </div>
    <div class="gw-pill"><span class="label">GW</span><span class="num" id="gwNum">—</span></div>
  </div>
</header>
<nav>
  <div class="nav-inner">
    <div class="nav-item active">Matchups</div>
    <div class="nav-item">Ladder</div>
    <div class="nav-item">Squads</div>
    <div class="nav-item">Admin</div>
  </div>
</nav>
<main>
  <div class="status-bar">
    <h1 class="section-title" id="sectionTitle">GW31 Fixtures</h1>
    <div class="bonus-badge badge-checking" id="bonusBadge">
      <div class="pulse-dot"></div><span id="bonusText">Checking…</span>
    </div>
  </div>
  <div id="appBody">
    <div class="loading-state">
      <div class="spinner"></div>
      <div class="loading-text">Fetching live FPL data…</div>
    </div>
  </div>
  <div class="meta-row" id="metaRow" style="display:none">
    <div class="refresh-bar">
      <span class="refresh-icon" id="refreshIcon">↻</span>
      <span>Auto-refreshes every 60 seconds</span>
    </div>
    <div class="last-updated" id="lastUpdated"></div>
    <div class="api-note">Live data from <span>FPL API</span> · <span>Raw squad totals</span> · Best XI engine in Step 3</div>
  </div>
</main>
<div class="bottom-nav">
  <div class="bn-item active"><div class="bn-icon">⚽</div><div class="bn-label">Matchups</div></div>
  <div class="bn-item"><div class="bn-icon">📊</div><div class="bn-label">Ladder</div></div>
  <div class="bn-item"><div class="bn-icon">👥</div><div class="bn-label">Squads</div></div>
  <div class="bn-item"><div class="bn-icon">⚙️</div><div class="bn-label">Admin</div></div>
</div>

<script>
const TEAMS = [
  { id:1, name:"The Legend of Porro and Yoro",    gk:["Arsenal","Fulham"],         def:[683,568,106,473,575,228,7],   mid:[119,237,414,387,20,487,242], fwd:[430,283,691,671] },
  { id:2, name:"A Sarr is Born",                  gk:["Man City","Man Utd"],        def:[371,475,41,293,316,77,507],   mid:[381,413,582,267,427,50,350], fwd:[249,178,136,808] },
  { id:3, name:"Bread and Rutter",                gk:["Brighton","Brighton"],       def:[370,256,72,694,476,317,477],  mid:[266,235,158,486,241,699,488],fwd:[661,654,311,100] },
  { id:4, name:"Iwobi Noni Kenobis",              gk:["Everton","Crystal Palace"],  def:[6,224,5,440,292,478,107],     mid:[450,324,18,26,390,21,418],   fwd:[31,215,785,338] },
  { id:5, name:"Ndiaaaye will always love Diouf", gk:["Brentford","Bournemouth"],   def:[260,569,684,291,442,603,226], mid:[16,615,236,160,299,417,329], fwd:[681,97,337,526] },
  { id:6, name:"Muaniball",                       gk:["Liverpool","Aston Villa"],   def:[258,505,411,74,225,257,148],  mid:[17,485,717,84,82,515,83],    fwd:[596,666,310,726] },
  { id:7, name:"Gittens Car Wash",                gk:["Newcastle","Leeds"],         def:[443,725,113,374,407,110,36],  mid:[382,452,708,453,303,120,157],fwd:[64,250,560,791] },
  { id:8, name:"Bowenie Babies",                  gk:["Chelsea","Sunderland"],      def:[261,373,8,531,295,151,408],   mid:[384,449,47,796,517,457,660], fwd:[714,30,135,624] },
];
const MATCHUPS = [{home:5,away:8},{home:3,away:4},{home:1,away:6},{home:2,away:7}];
const FPL_CLUBS = {1:"Arsenal",2:"Aston Villa",3:"Bournemouth",4:"Brentford",5:"Brighton",6:"Chelsea",7:"Crystal Palace",8:"Everton",9:"Fulham",12:"Liverpool",13:"Man City",14:"Man Utd",15:"Newcastle",16:"Nott'm Forest",18:"Spurs",19:"West Ham",20:"Wolves",21:"Leeds",22:"Sunderland"};

let playerMap={}, liveScores={}, gkBest={}, currentGW=31, dataChecked=false;

// Calls our own Flask backend — no CORS issues
async function apiFetch(path) {
  const res = await fetch(path);
  if (!res.ok) throw new Error(`Server error: ${res.status}`);
  return res.json();
}

function getTeamScore(team) {
  let gkPts = 0;
  team.gk.forEach(clubName => {
    const fplId = parseInt(Object.entries(FPL_CLUBS).find(([,n]) => n === clubName)?.[0]);
    if (fplId && gkBest[fplId] !== undefined && gkBest[fplId] > gkPts) gkPts = gkBest[fplId];
  });
  const outfield = [...team.def, ...team.mid, ...team.fwd];
  let total = gkPts, scored = 0;
  outfield.forEach(pid => {
    const pts = liveScores[pid] ?? 0;
    if (pts > 0) scored++;
    total += pts;
  });
  return { total, gkPts, scored };
}

function renderMatchups() {
  const html = MATCHUPS.map((m, i) => {
    const home = TEAMS.find(t => t.id === m.home);
    const away = TEAMS.find(t => t.id === m.away);
    const hs = getTeamScore(home), as = getTeamScore(away);
    const hc = hs.total > as.total ? 'winning' : hs.total < as.total ? 'losing' : 'drawing';
    const ac = as.total > hs.total ? 'winning' : as.total < hs.total ? 'losing' : 'drawing';
    const chip = dataChecked
      ? `<div class="fin-chip">FT ✓</div>`
      : `<div class="live-chip"><div class="dot"></div>Live</div>`;
    return `
      <div class="matchup-card">
        <div class="card-top"><span class="match-label">Match ${i+1} of 4</span>${chip}</div>
        <div class="card-body">
          <div class="team-side left">
            <div class="team-name">${home.name}</div>
            <div class="gk-detail">GK: ${home.gk.join(' / ')}</div>
            <div class="player-count">${hs.scored} scoring · GK ${hs.gkPts}pts</div>
          </div>
          <div class="score-block">
            <span class="score ${hc}">${hs.total}</span>
            <span class="score-sep">–</span>
            <span class="score ${ac}">${as.total}</span>
          </div>
          <div class="team-side right">
            <div class="team-name">${away.name}</div>
            <div class="gk-detail">GK: ${away.gk.join(' / ')}</div>
            <div class="player-count">${as.scored} scoring · GK ${as.gkPts}pts</div>
          </div>
        </div>
        <div class="card-footer">
          <span class="footer-hint">Raw totals · Best XI filter in Step 3</span>
          <span class="footer-arrow">›</span>
        </div>
      </div>`;
  }).join('');
  document.getElementById('appBody').innerHTML = `<div class="matchups-grid">${html}</div>`;
}

function updateHeader() {
  document.getElementById('gwNum').textContent = currentGW;
  document.getElementById('sectionTitle').textContent = `GW${currentGW} Fixtures`;
  const badge = document.getElementById('bonusBadge');
  badge.className = dataChecked ? 'bonus-badge badge-confirmed' : 'bonus-badge badge-pending';
  badge.innerHTML = dataChecked
    ? '<div class="pulse-dot"></div><span>Bonus Confirmed</span>'
    : '<div class="pulse-dot"></div><span>Bonus Pending</span>';
}

async function loadAll() {
  const icon = document.getElementById('refreshIcon');
  if (icon) icon.classList.add('spinning');
  try {
    const bootstrap = await apiFetch('/api/bootstrap');
    const currentEvent = bootstrap.events?.find(e => e.is_current) || bootstrap.events?.find(e => e.is_next);
    currentGW   = currentEvent?.id ?? 31;
    dataChecked = currentEvent?.data_checked ?? false;
    bootstrap.elements?.forEach(p => {
      playerMap[p.id] = { name: p.web_name, type: p.element_type, teamId: p.team };
    });

    const live = await apiFetch(`/api/live/${currentGW}`);
    liveScores = {}; gkBest = {};
    live.elements?.forEach(e => {
      const pts = e.stats?.total_points ?? 0;
      liveScores[e.id] = pts;
      const p = playerMap[e.id];
      if (p?.type === 1 && (gkBest[p.teamId] === undefined || pts > gkBest[p.teamId])) {
        gkBest[p.teamId] = pts;
      }
    });

    updateHeader();
    renderMatchups();
    document.getElementById('metaRow').style.display = 'flex';
    document.getElementById('lastUpdated').textContent =
      `Last updated: ${new Date().toLocaleTimeString('en-GB',{hour:'2-digit',minute:'2-digit',second:'2-digit'})}`;
  } catch(err) {
    document.getElementById('appBody').innerHTML = `
      <div class="error-state">
        <strong>Could not load FPL data</strong><br>${err.message}
        <code>Make sure the Flask server is running: python app.py</code>
      </div>`;
  } finally {
    if (icon) icon.classList.remove('spinning');
  }
}

loadAll();
setInterval(loadAll, 60_000);
</script>
</body>
</html>
