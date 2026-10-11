# Brainstorm record — product and business ideas

Chris and Claude, Saturday 2026-10-10 to Sunday 2026-10-11. Rebuilt 2026-10-11; the first version was cut off mid-write.
Short versions of the three product ideas are in Notes World (tag "new business ideas", under "big ideas"), and the wider list is
in `business-ideas-list.md`.

**How to read this:** "Chris" = decisions and facts he stated. "Claude" = my cautions and suggestions. Points marked
*(general knowledge)* were not researched and need checking.

## Context
- Rehm KI Consulting: freelance (§18), solo, started 1 Oct 2026 under a Gründungszuschuss, near Augsburg.
- Capacity: up to 25 billable days a month if the work exists.
- Defense work is acceptable. Customers: small and medium firms in Germany first, but nothing is ruled out.
- Chris wants AI-driven process streamlining, not plain software development.

## Decision summary
| Idea | Horizon | Decision |
|---|---|---|
| 1. Geopolitical simulator / predictor | long-term | Research project first. Write the validation protocol before any code. |
| 2. Third-party business verifier | long-term | Not brainstormed in depth. Narrow to a company-level check first. |
| 3. Recurring penetration-testing service | now | Prove the engine first, then sell a managed service, then productize only if demand shows. |
| Process X-ray (existing project `~/ppp2/process-analysis`) | now | Run a first real client pilot; start with a hybrid (free or discounted first client, paid sprints after). |

---

## Idea 1 — Geopolitical simulator / predictor

**Concept (Chris):** give an AI agent information on key people (for example Putin, Trump, Zelensky, Netanyahu, or business
leaders), run 10–30 simulations of a situation, and look at the outcome after 3, 6 and 12 months. Customers: leaders of major
corporations, the German government, state governments, the EU.

**Chris's refinement:** test the agent on situations where the real outcome is known, compare its predictions to what happened,
and narrow it down. Use Jev (TypeSafe's classification and probability tool) to score possible outcomes and build a decision or
probability tree, instead of free-form LLM output.

**Main risk (Claude): contamination.** The model already knows how past events turned out, so testing on history can look like
skill and prove nothing. Fixes: (1) use only events after the model's knowledge cutoff, (2) disguise past events (names, dates,
places), (3) forward-test: log timestamped predictions now and score them when reality arrives. Jev is also a model, so its
probabilities must be checked against real outcomes with a scoring rule (Brier score, calibration).

**Honest framing:** until validated, sell it as scenario exploration (wargaming, red-teaming), not as forecasting.

**Possible funding and support (nothing applied for):** CIHBw pitch, NATO DIANA (annual call June 2027, dynamic challenges any
time), Forschungszulage (agent fidelity is real R&D; confirm with the Steuerberater), BayVFP with an Augsburg professor.

**Next steps:** write the validation protocol (data split, scoring rule, forward-test log), pick 3–5 test situations after the
model cutoff, check how Jev's calibration behaves on them.

## Idea 2 — Third-party business verifier

**Concept (Chris):** show that a business or website is what it says it is: who owns the site, who runs it, and a comparison of
what the site says about itself with independent research the site doesn't mention.

**Cautions (Claude, general knowledge):** compiling personal histories of individuals is a GDPR trap in Germany; WHOIS ownership
data is mostly redacted now; "know your business" checks already exist (for example Creditreform, Dun & Bradstreet).

**Viable core:** compare a site's claims with public registers (Handelsregister, Impressum, VAT ID, domain age) and produce a
company-level trust report, with no profiles of private individuals.

**Next steps:** pick one customer type and one verifiable claim; test by hand on about 20 websites before any build.

## Idea 3 — Recurring penetration-testing service

*This section is deliberately short. The first, longer write-up of it was stopped by a safety check on 2026-10-10 and has not
been re-created here. The complete notes are in Notes World: item "daily-weekly-monthly- penetration testing service for data
leaks", under "big ideas".*

- **Status (Chris):** he runs a stack of tools and models against his own apps and his own VPS only. Never against anyone
  else's systems without authorization.
- **Plan:** (1) prove the engine with a controlled benchmark, (2) sell a managed service to solo founders, small SaaS builders
  and Mittelstand, (3) build a self-serve version only if demand shows. The benchmark protocol has not been written.
- **Model hosting (Chris):** the models run on OpenRouter, not locally. Data must therefore be scrubbed before it leaves.
  Chris wants a local AI to do the scrubbing and has ideas for it. That need is also idea 1 in the wider list (privacy gateway).

---

## Process X-ray (project `~/ppp2/process-analysis`)

Chris's existing project. Thesis (README): every process step is a fossil of a constraint that used to be expensive; ask which
constraint shaped each step and whether it still binds. Built so far: an analyzer scored against two synthetic processes with
hidden answer keys, a hosted web app with invite-only accounts, a viewer, and a workbench that runs claim extraction through
several providers with names hidden first. Not built: browser-driven interviews. By the README, no real client has been analysed.

**Decision (Chris, 2026-10-11):** run a first real pilot. Claude suggested a hybrid: free or discounted first client in return for
a written case study, then paid fixed-price sprints. Candidate firms (not yet researched) are in `pilot-shortlist.md`.

**Pilot conditions to settle first:** payment and the written return, interviewee consent and the works council if one exists,
which model providers are allowed for this client plus a data-processing agreement, and how savings will be checked.

## Open questions
- The benchmark protocol for the penetration-testing service (not written).
- Chris's ideas for the local scrubbing, and which data must be removed (see privacy gateway in `business-ideas-list.md`).
- Whether to research the top three pilot firms.
- Novelty check for every idea before building.
