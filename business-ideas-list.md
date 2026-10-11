# Business ideas brainstorm — general list

Saturday 2026-10-10, Chris and Claude. Goal: online businesses (maybe with an offline part) where AI is necessary.
Chris's reaction: all nine are interesting. Customers: small and medium firms in Germany, or a mix that pays fastest;
public sector, defense and consumers are also acceptable ("ruling somebody out is not the way I think").

**Caveat:** I have not researched the market. "Existing pieces" are from general knowledge and must be checked
before anyone builds anything.

| # | Idea | AI is needed for | Existing pieces (unverified) | Status |
|---|---|---|---|---|
| 1 | **Privacy gateway for AI use.** A local model finds personal and confidential data in a prompt, swaps it for placeholders, sends the safe text to a cloud model, restores values in the answer, and keeps an audit log. | Context-aware detection of sensitive data | Open-source PII detectors (e.g. Presidio) and commercial tools | Chris: "interesting"; he already has ideas for the local scrubbing |
| 2 | **Process X-ray for small firms.** Take a company's incoming data, map its workflows, rank what to automate, estimate savings, flag subsidies. | Reading messy inputs, finding workflows | Process mining exists for large enterprises | **Chris already started a project called "process analysis" that does this.** Added to Notes World big ideas. To discuss further. |
| 3 | **Funding and tender copilot for micro-firms.** Monitors sources, matches a company profile, drafts German applications and bids with a human check. | Matching, drafting | Funding databases and some AI tender tools exist | Core partly built (this folder) |
| 4 | **Tender-response checker.** Reads tender documents, builds a checklist of required proofs and forms, flags formal errors in the draft before submission. | Document reading, checking | AI tender tools appear in search | Not started |
| 5 | **Spec-writing assistant for municipalities.** Helps buyers write neutral specs, estimate quantities, do market research. | Drafting, research | Unknown | Not started; slow public sales cycle |
| 6 | **German paperwork copilot.** Reads authority, insurance and medical letters, explains them, tracks deadlines, drafts replies and claims. Local-first. | Reading letters, drafting | Unknown | Chris: "interesting" |
| 7 | **Independent model-selection audit.** Uses Chris's task-versus-model data to tell companies which model to use for which job on cost and quality. | Evaluation | Public leaderboards, evaluation tools | Not started |
| 8 | **Craft-business capture.** Photo of handwritten measurements or delivery notes becomes structured data for accounting or ERP. | Handwriting and layout reading | Probably some | Not started |
| 9 | **Business-decision pre-mortem.** Test a pricing or strategy move against simulated customers, competitors and regulators; validate on forward-logged predictions. | Simulation, scoring | Related to the geopolitical simulator idea | Not started |

## Claude's top three for Chris (his situation: solo, 25 billable days a month, Mittelstand around Augsburg)
1. **#1 Privacy gateway.** Needed anyway for the pen-testing service (cloud models run via OpenRouter, so data must be
   scrubbed first). Reusable across projects. Government and defense need it.
2. **#2 Process X-ray.** Matches his consulting offer and capacity. Revenue without a big build.
3. **#3 Funding and tender copilot.** Core already exists here; least novel.

## Open questions
- ~~Where is the "process analysis" project?~~ Answered: `~/ppp2/process-analysis` (README, parts of PRIVACY and PHILOSOPHY read 2026-10-10). Hosted web app, analyzer scored on synthetic processes, workbench with a provider layer and pseudonymisation. No real client process analysed yet per the README. Not yet read: ARCHITECTURE, CAPTURE, EVAL, the code.
- For #1: what are Chris's ideas for the local scrubbing, and which data must be removed?
- Novelty check for each idea before building (search the German market and the usual launch sites).
