# AI-Native Travel OS — Complete Build Plan (Superior to Triple Intro)

## 1) Product thesis
Build a travel product that feels like a **personal operating system for trips**, not a static itinerary generator.

What “AI-native” means here:
- Not chat-first; starts with destination/date intent and known preferences.
- Continuously learns from user behavior and media saves.
- Produces plans that are easy to edit in direct-manipulation UI (timeline + map + board).
- Handles logistics + money + group coordination end-to-end.

## 2) Why users dislike existing tools (problem framing)
Pain points to solve decisively:
1. **Plan quality and personalization are weak.** Users already have taste signals in Instagram/TikTok/maps saves, but current apps ignore them.
2. **Schedule editing is frustrating.** Search, swap, reorder, and time optimization are too manual and brittle.
3. **Money settlement creates social friction.** Expense input is slow, split logic is limited, and repayment follow-up is awkward.

## 3) Product pillars (the moat)
1. **Taste Graph ingestion engine**
   - Ingest saved content and infer user preference vectors.
   - Aggregate individual vectors into a group utility model.
2. **Pro itinerary workspace**
   - Fast direct editing with hard constraints and AI-assisted optimization.
3. **Settlement OS**
   - Installments, multi-currency correctness, automatic nudges, and minimal-transfer settlement.
4. **Live operations layer**
   - Re-plan in response to weather, delays, closures, and budget drift.

## 4) Experience blueprint (not chat-first)

### 4.1 Entry flow (under 90 seconds)
Entry cards:
- Destination, dates, party type, pace
- Budget target and must-have/must-avoid
- Accessibility and dietary constraints
- Import preference sources (Instagram saves, links, map lists)

Immediate output:
- 3 starter trip styles (Balanced / Food-first / Landmark+Hidden)
- Cost/time confidence score
- “Missing data” prompts for quick refinement

### 4.2 Preference ingestion (key differentiator)
Sources:
- Instagram saved posts/reels collections
- TikTok favorites
- Google Maps saved places/lists
- URL paste and screenshot import

Processing pipeline:
1. Extract entities (place, cuisine, activity, mood, price hints).
2. Enrich with geodata and venue metadata.
3. Create per-user embeddings and explicit preference tags.
4. Merge to group Taste Graph with conflict weighting.

Outputs:
- Ranked place candidates by destination/daypart.
- Explainability chips: “Why suggested: similar to 18 saved spots + low queue + sunset view.”

### 4.3 Itinerary workspace (fixing schedule editor pain)
Core layout:
- Left: day timeline (time blocks)
- Center: map and route overlays
- Right: card detail + alternatives

Critical interactions:
- Drag place cards across days/time slots.
- Smart slot insert (“fill 2-hour gap near current route”).
- Natural command bar (“replace dinner day 3 with top ramen near Shibuya under $25”).
- Lock constraints (must-do, fixed booking windows, non-movable items).
- One-click re-optimization with preserved locks.

Search that actually works:
- Semantic + structured filters (vibe, price, queue risk, travel radius, accessibility).
- “Best nearby now-open options” with confidence + transit time.

### 4.4 Group collaboration
- Roles: owner, planner, editor, treasurer, viewer.
- In-line votes/polls for unresolved slots.
- Change approvals for sensitive edits.
- Decision summaries (“3/5 prefer sushi; selected option minimizes detour by 22 min”).

## 5) Settlement OS (fixing money tracking pain)

### 5.1 Fast capture
- One-tap add expense
- OCR receipt parse
- Voice capture (“I paid 48 dollars for taxi, split 3 ways except Alex”)
- Smart defaults by category/vendor/person

### 5.2 Flexible split engine
Split modes:
- Equal
- Weighted by participant
- Itemized per person
- Category policies (e.g., lodging equally, alcohol custom)

### 5.3 Installment-aware settlements
- Per-debtor installment plans (date, amount, cadence).
- Auto-recompute balances after partial payments.
- Minimize transfers while honoring installment schedules.

### 5.4 Multi-currency + reminders
- Store original currency and settlement currency.
- Daily FX rate snapshots and optional locked rate at purchase time.
- Reminder automations:
  - Pre-due reminder
  - Due-day reminder
  - Overdue escalation
  - “Payment received” confirmations

### 5.5 Trust and dispute UX
- Immutable ledger event history.
- Adjustment requests with receipts and comments.
- Export to CSV/PDF and clear payoff graph.

## 6) “Superior” features beyond baseline
1. **Disruption AI:** weather/closure/delay detection + one-tap re-plan.
2. **Booking intelligence:** price watch and alert when better alternatives exist.
3. **On-trip daily briefing:** route, reservations, weather, budget burn, reminders.
4. **Offline mode:** cached map areas and day plans.
5. **Safety layer:** emergency cards, embassy info, local emergency numbers.
6. **Post-trip recap:** timeline + spend report + reusable preference profile.

## 7) Technical architecture

### 7.1 Client
- Web: Next.js + TypeScript
- Mobile: React Native (shared domain logic)
- Real-time collaboration via CRDT
- Map SDK + route visualization

### 7.2 Services
1. Auth + group membership
2. Preference ingestion + entity extraction
3. Place graph and ranking/retrieval service
4. Itinerary optimization service
5. Ledger + settlement computation service
6. Notification orchestration service
7. Analytics + experimentation service

### 7.3 Data model highlights
- UserPreferenceProfile (embeddings + explicit tags + confidence)
- GroupPreferenceProfile (member weights + conflict map)
- TripPlan (days, slots, constraints, provenance)
- ExpenseLedger (expense events, splits, payments, installments)

### 7.4 AI stack
- LLM orchestration for reasoning + tool calling.
- Retrieval-first generation with source grounding.
- Rule-based post-validation for itinerary feasibility and money math.

## 8) Delivery roadmap

### Phase 0 (2 weeks) — Foundations
- Product instrumentation, schema design, design system, map primitives.

### Phase 1 (8-10 weeks) — Must-win MVP
- Intent-first setup
- v1 itinerary generation + visual editor
- v1 expense capture + equal/custom splits
- basic reminders

### Phase 2 (8 weeks) — Differentiators
- Instagram/map/tiktok import pipeline
- Taste Graph personalization
- Installment + FX settlement engine
- Polling + collaboration workflows

### Phase 3 (10 weeks) — Moat
- Live disruption replanning
- Booking intelligence and price watch
- Advanced dispute and audit tools
- Post-trip intelligence

## 9) Quality gates (definition of done)

### Planning quality
- >=95% opening-hours valid placements
- <=10% route-overrun errors
- >=25% improvement in preference-match score vs baseline recommender

### Editing usability
- <=3 clicks median for replace action
- >=90% successful edit-task completion in usability tests

### Settlement correctness
- 0 invariant violations in ledger consistency suite
- deterministic rounding behavior across currencies
- installment schedule replay tests pass

## 10) Risks and mitigation
1. **Platform API limits (Instagram, TikTok).**
   - Support import-by-export and link parsing fallback.
2. **Hallucinated suggestions.**
   - Retrieval grounding + provenance display + confidence thresholds.
3. **Settlement edge-case complexity.**
   - Strict double-entry style event model + property-based tests.
4. **Group decision deadlocks.**
   - Poll expiry + default tie-break policies.

## 11) KPI framework
Primary:
- Time to first acceptable itinerary
- Weekly active group trips
- Itinerary edit retention
- Settlement completion within 7 days

Secondary:
- Import connection rate
- Re-plan acceptance rate
- Reminder response rate
- NPS after trip completion

## 12) Launch strategy
1. Start with friend-group city trips (highest coordination pain).
2. Positioning: “Plan + Edit + Settle in one AI-native workspace.”
3. Migrate users from split-only and itinerary-only apps with import tools.
4. Growth loops: shareable trip recaps and transparent savings metrics.

## 13) Execution checklist (immediate next steps)
- Finalize PRD + user stories by persona (planner, treasurer, participant).
- Produce clickable design prototype for the itinerary workspace.
- Stand up place graph + itinerary feasibility APIs.
- Build ledger engine first with full invariants before UI polish.
- Run pilot with 20 travel groups and iterate on edit/money friction.

---

### End state
A “hell of an app” is one where users say:
- “It already knew my vibe from my saved content.”
- “Editing took seconds, not an argument with AI.”
- “Nobody fought about money—installments and reminders just worked.”
