# MGP Fantasy League — rules, infra and runbook

This file is the single source of truth for how the league works and how Claude operates the app. Update it in the SAME commit as any change that makes it stale. Never put live state (squads, scores, locked GWs) here; query Supabase / index.html instead.

Owner: Josh (non-developer). Claude is developer and operator. Free-tier only: the whole stack must stay at £0/month.

## Infrastructure
- GitHub braveyboy/mgp-fantasy, branch main. Files: app.py, templates/index.html, requirements.txt, Procfile.
- Render web service mgp-fantasy (srv-d75o3dudqaus73bfma80, workspace tea-d75npf1aae7s73cr54qg), free plan, Auto-Deploy On Commit: a push to main goes live in about a minute. Free tier sleeps after 15 min idle (~60s cold start).
- Supabase project cmiqgbspksvrmfvyamdx (ap-northeast-1). Flask connects through DATABASE_URL (Session pooler). Free projects auto-pause after ~7 days of no activity: if the site shows DB errors, check project status and restore.
- Render env vars: DATABASE_URL, DRAFT_PIN (commissioner PIN for the Draft tab). Never print or commit values.
- Dependencies are pinned in requirements.txt and Python in .python-version (3.14.3). To upgrade, change the pins deliberately, deploy, and check the Render build and /api/health.
- Keep-alive: cron-job.org pings /api/health about every 10 min. If it is dead the site still works, just with cold starts.
- FPL API is blocked from Claude's sandbox. Use the vaastav mirror for player data: raw.githubusercontent.com/vaastav/Fantasy-Premier-League/master/data/<season>/players_raw.csv and teams.csv (event_points can be stale mid-GW).

## How Claude works on this repo
1. Before any code edit: pull the latest main, run git log -5, and state the latest commit SHA and date at the start of the reply. Never treat an attached or uploaded file as the source of truth.
2. Classify the request:
   - DATA fix (wrong player in a slot, GK club, score override, lock) -> change the Supabase row directly. No code change.
   - CODE change -> edit the repo, validate, summarise, push to main, confirm the Render deploy is live.
   - QUESTION / ANALYSIS (recaps, undrafted-player lists, previews) -> read-only.
3. Data-fix protocol: apply simple slot fixes and report exactly what changed and how to undo it. Ask first if the fix touches a locked GW, a draft in progress, a GW whose lock is pending, or more than 2 rows. Never change locked_gws or gw_snapshots without Josh's explicit say-so.
4. Validate before pushing: python -m py_compile app.py; extract the inline <script> from templates/index.html and run node --check on it.
5. After pushing: check the Render deploy for the new commit is live; if it fails, read logs and fix or roll back.
6. Prefer targeted edits; hand over whole files only if pushing is unavailable.

## Data model (read before touching squads)
- A team's squad = DEFAULT_TEAMS in templates/index.html (hardcoded, real FPL element IDs for the season) PLUS rows in the Supabase squads table, which are OVERRIDES keyed by team_id + position (def1..def7, mid1..mid7, fwd1..fwd4). GK clubs: gk_clubs overrides DEFAULT_TEAMS gk. Always combine both to find who owns a player.
- Negative IDs are PENDING_PLAYERS placeholders (not yet in FPL); swap them for real IDs via Team Admin or a squads row.
- Tables: squads, gk_clubs, gw_snapshots (source of truth for locked scores), score_overrides, locked_gws, void_gws, draft_sessions, draft_picks. RLS is ENABLED on all of them (the app connects as the postgres role, which bypasses RLS). Any table a future feature adds via init_db must also get RLS enabled by a Supabase migration.
- Endpoints: /api/squads (GET), /api/squads/<team_id> (POST slot), /api/squads/<team_id>/gk (POST), /api/snapshot, /api/override, /api/bootstrap, /api/live/<gw>, /api/fixtures/<gw>, /api/draft (+ /start /pick /end /override; PIN on start/end/override), /api/health.

## League rules
- Private draft league, FPL scoring, no captain bonus. 8 teams. Each team: DEF/MID/FWD players plus two GK CLUBS (not individual keepers).
- Best XI, auto-picked each week: 1 GK + min 3 DEF + 3 MID + 1 FWD + 3 flex (best remaining outfield; no second GK).
- Outfield players in a double GW take two XI slots (one per match).
- GK score: for each GK club take the single highest-scoring keeper it used. In a double GW only the best SINGLE GAME counts (never combine games or keepers). The higher of the two clubs is the starting GK; the other club is the GK bench.
- Live GW: only players whose team has finished count toward the XI; others sit on the bench.
- No captain/vice. No free in-season transfers.
- Squad changes happen only via: agreed trades between managers, in-season drafts (aim for about one per month, not strict, started by the commissioner with the PIN; snake order, each pick drops one player and adds one, passes allowed), or the pre-season mini-draft. Team Admin and the Draft tab write to Supabase.
- Player moves club within the PL: stays with his owner. Player leaves the PL: stays with his owner, scores 0 until swapped via trade/draft.
- Ladder (GW1-35, round robin): win 3, draw 1, loss 0 on Best XI score. Order: points, then points-for, then goal difference (for minus against), then head-to-head result.
- Void GW: if fewer than 6 PL matches are played in a GW it is void (no result, ladder skips it, it never locks, and it counts as "done" for starting the finals). Josh tells Claude when a GW is void; Claude records it with `insert into void_gws (gw, note) values (N, 'reason');` in Supabase (undo: delete the row). There is deliberately no public endpoint for this. Only regular-season GWs are handled; if a finals GW (36-38) ever needs voiding, ask Josh what should happen.
- Finals: top 4 by ladder. GW36 Qualifying Final (1v2) + Elimination Final (3v4); GW37 Preliminary Final (QF loser v EF winner); GW38 Grand Final (QF winner v Prelim winner). No third-place playoff. A drawn finals match goes to the team with the higher total regular-season points-for.
- GW locking: a GW locks the moment FPL marks its bonus points final (events[].data_checked). Locking freezes each team's squad and Best XI score permanently. score_overrides exist for manual corrections.
  How it works today: the lock is performed by the browser. Any open tab re-checks every 60 seconds, and a fresh page load checks the last 3 GWs, so the GW locks as soon as someone has the site open after bonus is confirmed. If nobody opens the site, it stays unlocked and squad changes in that window would change the locked score, so avoid squad changes between a GW finishing and it locking. If a GW has not locked after bonus is confirmed, open the site; if it still does not lock, tell Claude to investigate (Claude cannot compute Best XI scores outside the browser yet; see "Potential future fixes").

## Potential future fixes (not started; pick up only when Josh asks)
1. Fully automatic GW lock (large). Today locking needs someone to have the site open (see GW locking above). To make it automatic, the Best XI scoring maths would be rewritten in Python on the server, plus a free timer (the existing cron-job.org job could call a new endpoint every ~15 min). It would check FPL for bonus-confirmed GWs and lock them even if nobody visits, and would also let Claude lock a GW on request.
2. Admin score-override screen (large). The backend /api/override already exists but there is no screen for it, so manual score corrections currently mean Claude writes to the score_overrides table. A screen would let Josh do it himself in the Admin tab.
3. Season data into the database (medium). Teams, fixtures and FPL IDs are hardcoded in index.html, so every pre-season needs a code edit. Moving them to Supabase would make rollover a data change.
4. Server-side protection for write endpoints (medium). The squad/snapshot/override endpoints have no authentication (accepted for a trusted league), and DRAFT_PIN falls back to a default in app.py when the Render env var is unset. Revisit if the site ever opens beyond the league.
5. Keep-alive resilience (small). cron-job.org pings /api/health every 10 min but cannot wake a sleeping service (it gets an instant 503), so an outage can get it auto-disabled. If that recurs: open the site in a browser, re-enable the job, or switch to a free monitor such as UptimeRobot.

## Change log of rule/code gaps closed
- 2026-11-01: lock now fires at bonus-confirmed (was: after next GW deadline); finals draws decided by regular-season points-for (was: ladder seed); head-to-head added to ladder tiebreaks; void GW support (void_gws table); dependencies pinned in requirements.txt and Python pinned in .python-version; RLS enabled on all Supabase tables; stale comments fixed.

## Season rollover checklist
1. Josh supplies rule changes, teams/managers/names, GK clubs, drafted squads, fixtures.
2. Replace DEFAULT_TEAMS, FIXTURES, PENDING_PLAYERS, STANDINGS_GW0 in index.html with the new season's real FPL IDs (verify against the vaastav mirror).
3. Export the old season (squads, gw_snapshots, ladder) to a saved file, then clear squads, gk_clubs, gw_snapshots, score_overrides, locked_gws, void_gws, draft_sessions, draft_picks.
4. Check the Render deploy is live, /api/health is OK, keep-alive is running, Supabase project is active.
