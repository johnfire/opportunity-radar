# Funding and Contract Sources — where to find paid innovation work, grants, pilots and tenders (DE / EU)

Document 3 of 3 in the opportunity system:
1. `opportunities.md` — open calls: what, 3–4 sentence summary, last application date, platform. *(not started)*
2. `submissions.md` — what we submitted, where, when, potential value, status. *(not started)*
3. **`funding-and-contract-sources.md` — this file.** Every place to look. The monitoring bot reads this list.

Version 1 — 2026-10-10. Written by Claude for Chris.

## How to read this file
- **Checked 2026-10-10** = I opened the URL or fetched the page content this session. "Reachable" = HTTP 200
  only; I did not read the page.
- **Unverified description** = from general knowledge, not read this session. Check before relying on amounts.
- **Pay type:** `contract` = you get paid to do the work. `grant` = funding for your own project.
  `lead` = market sounding / tender announcements; no money for the response itself.
  `loan` = repayable.
- **Monitor** = how a bot could watch it. `API` = a public data interface I have confirmed or believe exists.
  `scrape` = parse the HTML. `manual` = needs login or a real browser.

## A. Behzad's 10 links (from Notes World, tag "00- this week")
Source: project "research all the links Behzad gave you about getting work" (note says "do this asap",
due 2026-10-11). Each link was fetched on 2026-10-10. **Honest summary: most of these are startup
ecosystems and corporate "venture client" programmes, i.e. ways to get a pilot or customer. None of the
pages states a payment amount. Only SPRIND and KOINNO are close to SBIR-style calls.**

| # | Name | URL | What it is (from the page) | Open call / deadline | Pay type |
|---|---|---|---|---|---|
| 1 | KOINNOvationsplatz (your link points to one challenge) | https://app.koinnovationsplatz.de/challenges/6a47d075f321e1a16ee2ed1d | Your note says "somewhat like SBIRs". The linked challenge is HafenCity Hamburg's "Interaktive, digitale Anwendung für Dialog und Präsentation", **already finished** (winner announced Sept 2026). The platform itself is a market-sounding portal. | See `opportunities.md`; 5 open on 2026-10-10 | lead |
| 2 | GovTecHH (Hamburg) | https://startupcity.hamburg/de/trends-themen/govtechh | Hamburg's venture-client unit: matches startups' GovTech solutions to city administration needs; pilot projects. Contact: startups@sk.hamburg.de. | None listed; you pitch an idea by email | pilot (payment terms not stated) |
| 3 | BayStartUP | https://www.baystartup.de/ | Business-plan competitions (Munich, Northern Bavaria, Ideenreich, Swabia), coaching, investor network (said to place €50M+ a year in early-stage). | Registration page exists, no deadline on the homepage | network / feedback |
| 4 | BMW Group Startup Garage | https://www.bmwgroup.com/de/innovation/innovationsnetzwerk/startup-garage.html | BMW's venture-client unit: 4-month pilot projects to validate startup tech, aim to become a supplier. No equity. | None on the page; apply via bmwstartupgarage.com | pilot (payment terms not stated) |
| 5 | Bosch Startup Harbour (BIU) | https://www.bosch-business-innovations.com/stories/startupharbour-biu/ | Matchmaking between startups and Bosch, mentoring, pilot projects. Recent topics: software-defined manufacturing, generative AI and synthetic data, IT/digitisation. | None stated | pilot (payment terms not stated) |
| 6 | DB mindbox | https://www.dbmindbox.com/mindbox | Deutsche Bahn's startup hub in Berlin. 100-day programme, access to DB experts and real data. Claims 250+ projects, ~60% leading to follow-on cooperation. | One open call: "Flämingo Accelerator Cohort #3", **deadline 22 Nov 2026** (from the page; I couldn't confirm details elsewhere). Other calls expired. | programme / pilot |
| 7 | de:hub | https://www.de-hub.de/ | Network of 25 regional hubs linking Mittelstand/corporates with startups and research; corporate pilot programmes, startup finder, test spaces. | None; contact form | network |
| 8 | GovTech Deutschland | https://www.gov.tech/ | German GovTech organisation ("implementation partner for technology projects" for the state; 170+ members; mentions a €250M Bechtle framework contract for cloud and AI). Not a call board; useful for contacts and public-sector demand. **Correction: this is a German org, not the US magazine I assumed earlier.** | None | network / lead |
| 9 | SPRIND Challenges | https://www.sprind.org/taten/challenges | See section B. Five open calls on 2026-10-10; AI-Native Chip Design closes 30 Nov. | Yes | contract |
| 10 | UnternehmerTUM | https://www.unternehmertum.de/ | Munich innovation centre: pre-incubation, incubation, acceleration, founder advice, financing support, corporate innovation partnerships. | Not stated on the page | programme / network |

Link health 2026-10-10: all ten answered, except the BMW page, which failed one connection test but loaded
on a second fetch.

### Other candidates from the same Notes World tag (not Behzad's)
| Name | URL | Note |
|---|---|---|
| appliedAI Institute | https://www.appliedai-institute.de/en/ | In your "this week" tag. Not yet read. |
| Practical AI Act (EU) | https://practical-ai-act.eu/latest/showcase/ | In your tag, marked "read this". Not yet read; likely useful for EU AI Act positioning, not a call board. |

## B. Innovation challenges and paid R&D (closest to SBIR)

| Name | URL | What it is | Pay | Monitor | Status |
|---|---|---|---|---|---|
| SPRIND Challenges | https://www.sprind.org/en/challenges | German federal agency for breakthrough innovation. Staged competitions with fixed-price contracts up to several million euros. 5 open on 2026-10-10. | contract | scrape (the page lists status + deadline) | Checked 2026-10-10 |
| KOINNOvationsplatz | https://app.koinnovationsplatz.de/challenges | Public buyers post needs ahead of tenders (Markterkundung). No payment for answering; useful as a lead list and buyer-needs signal. | lead | **API**: `/api/challenges?page=1&pageSize=200&sort=-phases.start` returns all challenges as JSON, with `currentPhase`, deadlines and full text (confirmed 2026-10-10) | Checked 2026-10-10 |
| Cyber Innovation Hub der Bundeswehr | https://www.cyberinnovationhub.de/en/innovation/your-pitch-for-the-cihbw | Bundeswehr digital innovation unit. You send a short problem/solution pitch deck at any time; prototype contracts possible. Does not buy for the Bundeswehr itself. | contract (prototype) | manual (curl got HTTP 500; try in a browser) | Page found by search, not opened |
| Cyberagentur | https://www.cyberagentur.de/en/ | Federal agency for disruptive cyber/security research; runs challenges (e.g. SPECTRA with the CIHBw). | contract | scrape | Reachable (200) |
| NATO DIANA | https://www.diana.nato.int | NATO's dual-use accelerator and challenge programme. Check challenge calls and eligibility of your country and company. | grant/contract | manual (curl got 403) | Reachable only in a browser; unverified description |
| European Defence Agency | https://eda.europa.eu | EU defence agency; hosts defence innovation hub and calls. | grant/contract | scrape | Reachable (200); unverified description |
| EIC Accelerator | https://eic.ec.europa.eu | EU grant plus equity for companies with a deep-tech or innovation plan. Large, competitive, paperwork-heavy. | grant | scrape | Reachable (200); unverified description |
| EU Funding & Tenders Portal | https://ec.europa.eu/info/funding-tenders/opportunities/portal/screen/home | All Horizon Europe, Digital Europe and other EU calls, including pre-commercial procurement. | grant/contract | API (search interface exists; confirm before coding the bot) | Reachable (200) |
| Eurostars (EUREKA) | https://www.eurostars-eureka.eu | Funding for R&D-performing SMEs working with a partner from another participating country. | grant | manual (curl got 403) | Unverified description |

## C. German federal and state grants

| Name | URL | What it is | Pay | Monitor | Status |
|---|---|---|---|---|---|
| Förderdatenbank (Bund) | https://www.foerderdatenbank.de | Official database of federal, state and EU funding programmes. Search by topic, location and company size. | grant/loan | scrape | Reachable (200) |
| EXIST | https://www.exist.de | Founder grants tied to a university or research institution. Gründungsstipendium: up to a year; stipend €1,000–3,000/month. See notes in chat 2026-10-10: needs degree or research-job within the last 5 years; the university is the applicant. | grant | scrape | Checked 2026-10-10 |
| ZIM | https://www.zim.de | Federal innovation grants for SMEs, single projects or cooperation projects. | grant | scrape | Reachable (200); unverified description |
| BMFTR (research ministry) | https://www.bmftr.bund.de | Ministry that publishes research funding announcements (Förderbekanntmachungen). | grant | scrape | Reachable (200) |
| Projektträger Jülich (PtJ) | https://www.ptj.de | Agency that runs many federal programmes, including EXIST. | grant | scrape | Reachable (200) |
| DLR Projektträger | https://projekttraeger.dlr.de/de | Runs federal research and innovation calls. | grant | scrape | Reachable (200) |
| Prototype Fund | https://www.prototypefund.de | Funds open-source software prototypes by individuals and small teams in Germany. Check current amount and rules. | grant | manual (curl got 403) | Unverified description |
| Sovereign Tech Agency | https://www.sovereign.tech | German agency that pays for work on open-source infrastructure. | contract/grant | scrape | Reachable (200); unverified description |
| BAFA | https://www.bafa.de | Federal office; includes digitisation and consulting grants. | grant | scrape | Reachable (200) |
| KfW | https://www.kfw.de | Federal development bank; loans for digitisation and business growth. | loan | scrape | Reachable (200) |

## D. Bavaria

| Name | URL | What it is | Pay | Monitor | Status |
|---|---|---|---|---|---|
| Digitalbonus Bayern | https://www.digitalbonus.bayern | Bavarian grant for SME digitisation projects. Your own note of 2026-09-07 says up to €30k. | grant | scrape | Reachable (200) |
| LfA Förderbank Bayern | https://www.lfa.de | State development bank: founder and growth loans. | loan | scrape | Reachable (200) |
| BayStartUP | https://www.baystartup.de | Bavarian startup network: investor access, competitions, coaching. | lead/network | scrape | Reachable (200) |
| Bayern Innovativ | https://www.bayern-innovativ.de | Bavarian innovation cluster and funding advice. | lead/network | scrape | Reachable (200) |
| Vergabe Bayern | https://www.vergabe.bayern.de | Bavarian state procurement platform. | lead | scrape / manual (registration for documents) | Reachable (200) |

## E. Tenders (where contracts get published)

| Name | URL | What it is | Pay | Monitor | Status |
|---|---|---|---|---|---|
| TED (EU tenders) | https://ted.europa.eu/en/ | EU-wide public tender notices. | contract | API (TED has a public search API; confirm before coding) | Reachable (200) |
| service.bund.de Ausschreibungen | https://www.service.bund.de/Content/DE/Ausschreibungen/Suche/Formular.html | Federal tender search. | contract | scrape (possible RSS; confirm) | Reachable (200) |
| DTVP | https://www.dtvp.de | German public procurement platform used by many authorities. | contract | manual (registration) | Reachable (200) |
| evergabe-online | https://www.evergabe-online.de | Federal e-procurement platform. | contract | manual (registration) | Reachable (HTTP 400 on cookie check; open in a browser) |
| NLnet | https://nlnet.nl/propose/ | Dutch foundation funding open-source work with EU money; small grants. Check whether EU funding is currently running. | grant | scrape | Reachable (200); unverified description |

## F. Candidates I could not verify
- None right now. (Earlier I wrongly dropped govtechcampus.de because it redirects to gov.tech; that is GovTech Deutschland, now listed in section A.)

## G. Notes for the monitoring bot
- Highest-value, easiest first: KOINNOvationsplatz (clean JSON), SPRIND (status list), TED and EU Funding Portal (APIs to confirm), Förderdatenbank.
- Sites that blocked curl (403/500) need a real browser fetch or a different path.
- Each run should log: source, items seen, new items, and failures, and never submit anything. Submission stays a manual decision.
- A Hermes cron job fits (your Open Brain shows existing Hermes daily-briefing crons), or a scheduled Claude task. I haven't verified either setup.

## H. Scope decisions (Chris, 2026-10-10)
- **Art opportunities: excluded.** AI/tech/process work only.
- **Geography:** Germany and the EU/Europe are in. **USA is out.** UK and Switzerland were not mentioned;
  treat them as in scope only when a call is open to teams from Germany (SPRIND's chip challenge is, for example).

## I. Open questions for Chris
1. Which of Behzad's venture-client programmes (BMW, Bosch, DB, GovTecHH) do you want to approach? They
   expect a startup with a product to pilot; the draft Beihilfe response shows how I'd frame "no product yet".
