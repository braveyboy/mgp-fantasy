# MGP Fantasy League — rules, infra and runbook

This file is the single source of truth for how the league works and how Claude operates the app. Update it in the SAME commit as any change that makes it stale. Never put live state (squads, scores, locked GWs) here; query Supabase / index.html instead.

Owner: Josh (non-developer). Claude is developer and operator. Free-tier only: the whole stack must stay at £0/month.

## Infrastructure
- GitHub braveyboy/mgp-fantasy, branch main. Files: app.py, templates/index.html, requirements.txt, Procfile.
- Render web service mgp-fantasy (srv-d75o3dudqaus73bfma80, workspace tea-d75npf1aae7s73cr54qg), free plan, Auto-Deploy On Commit: a push to main goes live in about a minute. Free tier sleeps after 15 min idle (~60s cold start).
- Supabase project cmiqgbspksvrmfvyamdx (ap-northeast-1). Flask connects through DATABASE_URL (Session pooler). Free projects auto-pause after ~7 days of no activity: if the site shows DB errors, check project status and restore.
- Render env vars: DATABASE_URL, DRAFT_PIN (commissioner PIN for the Draft tab). Never print or commit values.
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
- Tables: squads, gk_clubs, gw_snapshots (source of truth for locked scores), score_overrides, locked_gws, draft_sessions, draft_picks.
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
- Void GW: if fewer than 6 PL matches are played in a GW it is void (no result, ladder skips it). Josh tells Claude when a GW is void and Claude records it.
- Finals: top 4 by ladder. GW36 Qualifying Final (1v2) + Elimination Final (3v4); GW37 Preliminary Final (QF loser v EF winner); GW38 Grand Final (QF winner v Prelim winner). No third-place playoff. A drawn finals match goes to the team with the higher total regular-season points-for.
- GW locking: a GW locks the moment FPL marks its bonus points final (events[].data_checked). Locking freezes each team's squad and Best XI score permanently. score_overrides exist for manual corrections.

## Known gaps between these rules and the code (fix in this order)
1. Lock trigger: code locks only after the NEXT GW's deadline passes, and only when someone opens the site. Change to fire at data_checked; keep "Claude locks GW X on request" as backup. Later: fully automatic server-side lock (needs the Best XI maths in Python plus a free timer, e.g. the existing cron-job.org).
2. Finals draws: code uses ladder seed (winnerOf in index.html). Change to higher regular-season points-for.
3. Ladder ties: code stops at goal difference. Add head-to-head.
4. Void GW: no support in code. Add a way for Claude to mark a GW void and have the ladder skip it.
5. Admin score-override UI (backend /api/override exists, no frontend).
6. Security hygiene: RLS is off on all Supabase tables (safe to enable: the app uses the postgres role, which bypasses RLS, and index.html has no Supabase client); DRAFT_PIN has a hardcoded fallback in app.py; squad/snapshot/override endpoints are unauthenticated (accepted for a trusted league); requirements.txt is unpinned.
7. Stale code comments in index.html reference "project instructions" and say finals auto-generation is still to build (it is built). Tidy when next editing.

## Season rollover checklist
1. Josh supplies rule changes, teams/managers/names, GK clubs, drafted squads, fixtures.
2. Replace DEFAULT_TEAMS, FIXTURES, PENDING_PLAYERS, STANDINGS_GW0 in index.html with the new season's real FPL IDs (verify against the vaastav mirror).
3. Export the old season (squads, gw_snapshots, ladder) to a saved file, then clear squads, gk_clubs, gw_snapshots, score_overrides, locked_gws, draft_sessions, draft_picks.
4. Check the Render deploy is live, /api/health is OK, keep-alive is running, Supabase project is active.
