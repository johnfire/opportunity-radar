# Submission – Challenge "The Next Generation of the Beihilfe App" (LBV Baden-Württemberg)

---

## 1. Company and solution approach
*(RF No. 1, 11)*

**Company.** Rehm KI Consulting, sole proprietorship (freelancer), Alpenstr. 3, 86836 Klosterlechfeld, Bavaria.
We are a small provider focused on AI-supported process automation. The owner is a computer
engineer with a background in hardware and software development
(verification at Intel, about six years of web development) and practical experience in
development with AI and with Java and TypeScript.

**Transparency up front (RF No. 1).** We do *not* have a market-proven Beihilfe app already in
productive use, and so we name no reference customers. We deliberately submit no product
evidence, but a solution approach and suggestions for shaping the service description. With this
we want to give the LBV market knowledge about possibilities that easily get lost in a
conventional procurement.

**Solution approach in brief.** An iOS/Android app and a web service that can be run in the
public sector's data centre. It receives receipts, buffers them, and hands them over through an
openly documented interface to the existing Beihilfe process. Distinguishing feature: **receipt
understanding already at capture**, with AI models that run entirely locally in the data centre
or on the device (no cloud AI, no transfer to third countries).

**Difference from other market participants (RF No. 11).**
1. Quality check and receipt recognition on the device, so that illegible, incomplete or wrongly
   assigned receipts are noticed before submission and not only at case handling.
2. Open interfaces (OpenAPI specification) for the app and the web service – no vendor lock-in.
3. Lean development designed around a few specialists with AI support; short iteration cycles for
   extensions.
We are (not yet) an established provider; these three points are our contribution, not market
leadership.

---

## 2. Accessibility and usability
*(RF No. 3, 8)*

**Accessibility (RF No. 8).** Target standard WCAG 2.2 AA / EN 301 549 / BITV 2.0, shown through
(a) automated tests during development, (b) manual testing with VoiceOver and TalkBack,
(c) testing with users with disabilities before every release and (d) a "declaration of
accessibility". Specifically: dynamic font sizes, sufficient contrast, complete screen-reader
labelling, operation without fine motor skills, voice and haptic cues during camera guidance,
plain language for help texts.

**User-friendly receipt capture (RF No. 3).** Live edge detection, automatic trigger on a sharp,
complete image, checks for blur, reflections, shadows and cut-off edges, multi-page capture and
immediate feedback ("closer/brighter please"). Afterwards, optionally, a plausibility hint (for
example "invoice amount not recognisable"). These hints are **supportive**; the decision on the
application remains entirely with the Beihilfe office.

**Experience with recognition rates (RF No. 3).** We bring practical experience in
development with AI and in Java and TypeScript, but have no recognition rates from productive
Beihilfe operation and therefore give no figure. We offer to **demonstrate the rate
measurably on a synthetic or anonymised test set of receipts provided by the LBV**, before any
procurement decision is made.

---

## 3. Time required and economic prerequisites
*(RF No. 6, 10)*

**Time required (RF No. 10) – our estimate, without guarantee.**
From award about **6–9 months to a pilot operation** with a limited group of users and
**9–12 months to regular operation**, including a security and data-protection concept,
connection to the Beihilfe process, accessibility testing, store approvals and migration from
the existing contract. AI-supported development mainly shortens the programming phase; approvals,
security sign-offs and store reviews cannot be shortened. We recommend a **transition phase with
parallel running** of the existing app so there is no gap in service.

**Pricing model (RF No. 6).** A **flat price independent of user and application numbers** would
be calculable for us: an annual flat fee for licence, maintenance and support, and separately a
framework with fixed day rates for further development. In line with the requirement "no
offers", we name no concrete prices.

**Staff (for context).** The roles mobile development, backend/operations and data
protection/IT security are currently **not filled**. If awarded, we scale the team as needed.
As a possible cooperation partner we see the company SoftB. For the Beihilfe
subject area we would involve an adviser with Beihilfe/private-health-insurance experience (see
section 5, RF No. 12).

---

## 4. Technical and organisational prerequisites, operation
*(RF No. 2, 4, 13, 14)*

**Architecture (RF No. 2).** Mobile app (iOS/Android, one shared code base) with an encrypted
local buffer for offline capture; central web service (containerised, stateless and scalable)
with test and production environments. **Operation in the public sector's data centre is
explicitly possible and preferred by us**; the solution has no dependence on cloud services
outside.

**Data protection (RF No. 4).** Health data under Art. 9 GDPR: data minimisation, end-to-end
secured transfer (TLS 1.3) and encryption at rest, role-based permission concept, **automatic
deletion after successful retrieval**, no tracking/analytics SDKs, no cloud AI services, data
protection impact assessment (Art. 35 GDPR) and data processing agreement as part of the
contract. The security concept follows BSI IT-Grundschutz.

**IT security standards (RF No. 14).** Following BSI IT-Grundschutz and OWASP MASVS/ASVS,
dependency and vulnerability scans in every build, signed releases, independent penetration test
before go-live. **We currently hold no ISO 27001 or BSI certification**; evidence can be provided
through operating partners or by obtaining certification if awarded.

**High availability (RF No. 13).** The LBV's target (≥ 99.5 % in 24/7 operation) is achievable
architecturally: stateless services, redundant instances, health checks and alerting, tested
recovery procedures. Actual availability depends substantially on operation and infrastructure
in the data centre; we would define the division of tasks clearly in the operating concept. We
have no operating track record from production.

**Sizing (calculated from the LBV's figures).** 2.4 million applications and 23 million pages per
year correspond on average to about 6,600 applications and 63,000 pages per day; for peak load
(for example the turn of the year) we plan for a multiple. Because data is deleted after
retrieval, storage needs stay low in continuous operation.

---

## 5. Best practices, experience from comparable projects
*(RF No. 5, 9, 12)*

**Experience in Beihilfe / private health insurance (RF No. 12).** We have **no prior experience
of our own** in the Beihilfe or PKV field. We would involve a subject-matter adviser.

**Notes on the tender (RF No. 9):**
1. **Consider splitting into lots** (§ 97 (4) GWB): opening app + web service, operation in the
   data centre and further development as separate lots opens the market to mid-sized providers
   and lowers the risk of a single provider.
2. **Open, documented retrieval interface** (OpenAPI) and handover of source code or escrow of
   the source code, so that app and web service stay replaceable later.
3. **Measurable acceptance criteria instead of vendor statements:** for example the share of
   receipts recognised without manual rework in the downstream OCR process, measured on a joint
   test set of receipts; accessibility as an acceptance test (BITV test).
4. **Resolve the tension in the requirements:** "market-proven standard solution, no individual
   development" and at the same time "continuous further development" and customising only fit
   together if configurability and extension points (design tokens, configuration instead of
   code) are required.
5. **Transition:** accounts, histories and store listings of the existing app should be able to
   be carried on; formulate switching without a gap in service as a requirement.
6. **New possibilities in receipt capture:** Today's multimodal models can already recognise
   receipt type and mandatory fields at capture. This can be run locally and should be provided
   for in the service description as an optional extension.

**Customising (RF No. 5).** The state's corporate design through design tokens/themes; texts and
help content configurable without programming effort; functional adaptations according to effort
within further development.

---

## 6. Extensibility and further development
*(RF No. 7)*

The web service encapsulates the business logic behind a versioned API, and the app is built
modularly (capture, application overview, communication). This allows the extensions named by
the LBV – **decisions and processing status in the app, correspondence with the Beihilfe office,
digital return channel** – to be added as independent modules without touching capture. Proposed
roadmap: (1) functional parity with today's app, (2) quality and plausibility hints at capture,
(3) status display, (4) messages/return channel. Scaling happens horizontally through additional
instances.

---

*Note: This feedback contains no offers within the meaning of procurement law and contains no
confidential content.*
