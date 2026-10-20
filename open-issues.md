# Open issues

**Plan (Chris, 2026-10-11):** nothing here is urgent this week. The SPRIND decisions, the pilot firms and the Prototype Fund thinking are all parked for **Saturday 17 Oct, 09:30** (calendar reminder created, with the 30-minute popup). Note that SPRIND Robotics closes Thu 22 Oct, five days after that review, so decide quickly or skip it.

Last updated: Sunday 2026-10-11. This is the one list of things that are open, waiting, deferred or that the radar cannot do.
Numbered so we can say "do 3". Remove an item when it is done and note it in the commit message.

## A. Submit-by dates (rule: send one week before the deadline)
| Call | Deadline | Submit by | Status |
|---|---|---|---|
| SPRIND Next Frontier Robotics | Thu 22 Oct 2026, 18:00 | — | **SKIPPED 2026-10-20 (Chris).** Track 1 needs a working industrial-grade robot; no concrete component idea or hardware partner commitment in time. Requirements kept in `sprind-robotics-application.md`. |
| SPRIND AI-Native Chip Design | Mon 30 Nov 2026, 11:00 CET | **Mon 23 Nov** | go / no-go not decided; Chris leans towards applying |
| SPRIND Measuring with Entanglement | Mon 9 Nov 2026 | Mon 2 Nov | Chris has a physics background; not decided |

Other SPRIND calls (Recoding Medicine 16 Oct, Engineering Microbial Consortia 16 Nov) were judged a poor fit (medicine, biology).
The radar lists all open SPRIND calls in every twice-monthly digest. One calendar reminder for the review on Sat 17 Oct 09:30 exists; there are no separate reminders per submit-by date.

## B. Sources the radar cannot read (check by hand)
These are also listed in every digest under "Von Hand prüfen / Check by hand" (`radar/config/manual_checks.txt`).
1. **Prototype Fund** — bot-protection page (bunny.net Shield, JavaScript check). Apply 1 Oct to 30 Nov 2026, 15:00 CET. See also item C3.
2. **ZIM** (zim.de) — blocks automated access; an application stop has been reported since July 2026; lifting hoped for early 2027.
3. **Förderdatenbank** (foerderdatenbank.de) — CAPTCHA for automated searches.
4. **DTVP** (dtvp.de, Deutsches Vergabeportal) — **registered as of 2026-10-20** (Chris). The earlier "Doppelregistrierung" problem is solved. The radar still cannot read it (login needed), so it stays a hand check. **Next (Sat 24 Oct or in a couple of days):** Chris logs in and we look at what DTVP offers: tender search with CPV filters (72*, 73*, 48*), saved searches or email alerts if it has them, and whether notices there are also listed on service.bund.de or TED (the radar already reads those). I never enter credentials; Chris logs in.
5. **Projektträger Jülich** (ptj.de) — was down (HTTP 504) on 2026-10-11; retry.
6. **CIHBw pitch page** — site was in the middle of a relaunch; recheck in November 2026.
7. **oeffentlichevergabe.de** — the national notice portal. Its Open Data API documentation needs a registration. service.bund.de partly covers the same notices.

The radar never works around CAPTCHAs, bot checks or logins.

## C. Decisions waiting on Chris
1. **SPRIND** go / no-go and team: see section A. Also which Augsburg professors and fields, for SPRIND or BayVFP.
2. **Pilot firms** for the process-analysis product: research done in `pilot-research.md` (Rupp, Riegele best); Chris picks one to approach.
3. **Prototype Fund**: Chris is thinking it over. It funds free and open-source software only, individuals only (freelancers), and it rules out "vibe coding" (AI as a tool is allowed, but no outsourcing of the work to people or machines). Chris sees the programme as anti-AI. No decision.
4. **Keywords**: review the first real digests (Thu 15 Oct twice-monthly, Sat 17 Oct weekly) and tune `radar/config/keywords.txt` (350 terms now; "digitalisierung" is noisy).

## D. Work to do
1. ~~Jev scoring pass~~ — **built 2026-10-11.** Every shown item gets a "Jev: lösbar? / solvable?" column (probability that a very small software and AI team could solve it, plus grant / service tender / goods). Advisory only: it never hides an item. The digest is sorted by this probability first, then keyword score (since 2026-10-11, at Chris's request). Spot-check: it ranked a KI-tool market sounding highest and a licence purchase lowest, but its range is narrow (about 20 % to 70 %) and it is weak on vague titles. Use it for ordering, not as a hard cut-off. Only title, buyer and a short summary are sent. Next: judge its quality after you have read a real digest.
2. **Seen-state gap**: the radar marks unmatched items as seen, so a keyword added later never resurfaces old items. Option: keep unmatched items unseen so they are re-evaluated each run.
3. **Pen-test benchmark protocol** — deferred by Chris on 2026-10-11 ("later"). Not written.
4. **`opportunities.md`** — the "days left" column goes stale daily.
5. **Push** — commits since the last push are local only; Chris says when.

## E. Waiting for others
1. **LBV Baden-Württemberg** — reply to the Beihilfe-App market sounding (submitted 2026-10-11). No payment, possible invitation to a follow-up talk.
2. **SoftB / Behzad** — named in the Beihilfe response as a possible partner; no commitment either way.
