# Opportunity radar — index and status

Last updated: Sunday 2026-10-11. This folder is a git repository (private, GitHub `johnfire/opportunity-radar`).

## The system
Three core documents track the funding and contract work:
1. `opportunities.md` — what is open now: description, last application date, platform, pay, fit.
2. `submissions.md` — what we submitted, when, and what it could be worth.
3. `funding-and-contract-sources.md` — every place to look. The planned monitoring bot reads this list.

Supporting documents:
| File | What it is |
|---|---|
| `fit-evaluation-2026-10-10.md` | Ranked fit of opportunities for Chris, which need a product, what was not scanned |
| `brainstorm-ideas.md` | Record of the three product ideas, the process X-ray project and the pilot decision |
| `business-ideas-list.md` | Nine online-business ideas with AI as a necessary part |
| `koinno-open-challenges.md` | Bilingual (EN/DE) list of the 5 open KOINNOvationsplatz challenges, English first, with a recommendation (look at the Beihilfe app, ignore the other four) |
| `koinno-open-challenges-de-en.md` | Same document, German first |
| `open-challenges.md` | **Master list** of open calls, one section per website (German first, English second), each with a shortlist. Sections: 1. SPRIND, 2. KOINNOvationsplatz, 3. CIHBw and Cyberagentur, 4. NATO DIANA, 5. EDA and EU defence innovation, 6. EIC, 7. EU Funding & Tenders Portal, 8. German funding programmes (Bavaria, ZIM), 9. Behzad's programmes, 10. Federal funding, 11. Tenders (TED, service.bund.de), 12. Eurostars, Innowwide, NLnet, 13. DTVP (registration problem), 14. Vergabe Bayern (nothing suitable), 15. evergabe-online, 16. Prototype Fund, 17. BMFTR, 18. oeffentlichevergabe.de (the national notice portal, many IT tenders); an appendix lists sources we are not pursuing; plus; a short list of calls with a stated problem and a grant sits at the very top a calendar of recurring dates at the end. Detailed earlier SPRIND version: git commit f6553e2 |
| `pilot-shortlist.md` | Six Augsburg-area firms as candidates for the first process-analysis pilot (not researched) |

Outside this repository: `~/Projects/koinno-beihilfe/` (draft response to the LBV Beihilfe-App market sounding, due Mon 12 Oct),
`~/ppp2/process-analysis` (the product, own repo), `~/ai-workzone/rehm-consulting/businesses-from-daily-brief.md` (firm register).
Also: Notes World "big ideas" entries and an Open Brain task-eval record.

## Decisions so far (Chris)
- Art opportunities are excluded; Germany and the rest of Europe are in; the USA is out.
- Defense work is acceptable.
- Capacity: up to 25 billable days a month if the work exists.
- The penetration-testing service is the fast product; the simulator and the verifier are long-term. Models run on OpenRouter, so
  data must be scrubbed before it leaves; Chris has ideas for a local scrubber.
- Process X-ray: run a first real pilot with a hybrid pricing approach.
- Organize the system before working on individual cases.

## Open decisions
1. Beihilfe-App response (due Mon 12 Oct): submit or not; company name, bracketed items, optional commitments
   (see `../koinno-beihilfe/REVIEW-NOTES.md`).
2. SPRIND AI-Native Chip Design (30 Nov): go or no-go, and who would be on the team.
3. Which Augsburg professors and fields, for BayVFP or SPRIND.
4. Research the top three pilot firms?
5. The pen-testing benchmark protocol (not written).
6. Whether to move `koinno-beihilfe/` into this repository.

## To do next, once the system is settled
- Refresh dates in `opportunities.md` (days left goes stale daily).
- Scan the sources not yet scanned (ZIM, tender portals, EU Funding Portal, EDA/EUDIS).
- Mark the Notes World project "research all the links Behzad gave you" as done when Chris agrees.
