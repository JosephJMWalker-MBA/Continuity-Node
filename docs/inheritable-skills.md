# Inheritable Skills — Future Design Note

**Status:** future framework hypothesis / not implemented in the Tier-1 reference runtime  
**Scope:** longitudinal memory → candidate reusable capability → governed inheritance

## Purpose

Continuity Node already preserves source material, interpretive lineage, review, dissent, and rebuildable derived state. A natural long-horizon extension is to ask whether repeated, reviewed patterns from a person's lived conversational history can become **candidate skills** that another authorized person may later use.

This note records that architectural possibility without claiming that the current runtime implements it.

The intended progression is:

```text
preserved conversation / lived source
    ↓
provenance-bearing interpretation
    ↓
repeated pattern candidate
    ↓
candidate skill
    ↓
explicit human review / ratification
    ↓
authorized inheritance or sharing
    ↓
recipient-specific projection
    ↓
use + observed outcome
    ↓
revision without rewriting ancestry
```

## Core separations

Do not collapse:

```text
remembered
!= interpreted
!= recurrent
!= wise
!= reusable
!= ratified
!= authorized for another person
!= permanently binding
```

Conversation frequency is not enough to establish a skill. A repeated habit may be incidental, context-bound, mistaken, or something the person would not intentionally teach.

A candidate skill therefore needs more than extraction. It needs provenance, scope, counterexamples, governing conditions, review, and an explicit authorization event.

## Candidate skill record

A future interoperable skill projection should be able to preserve or reference, at minimum:

- skill identity and version;
- human-readable purpose;
- source lineage or source-set identity;
- principles or claims the procedure depends on;
- procedure / decision steps;
- applicability conditions;
- exclusions and known failure cases;
- unresolved questions;
- authority / ratification state;
- intended recipients or sharing scope;
- amendment and supersession lineage;
- evaluation evidence;
- external capabilities the skill may request.

The exact schema is unresolved. This list is a design requirement, not a claim that Continuity Node should own a universal skill ontology.

## Authority and inheritance

A historical person's view may remain intelligible without remaining authoritative forever.

The architecture should preserve:

```text
historical authorship
historical rationale
historical standing
current recipient adoption
current authority
```

as distinguishable properties.

A parent may authorize a teaching skill for a child. The same artifact should not silently retain identical authority when that child becomes an adult, when conditions change, or when a later generation encounters it.

Inheritance should therefore support **received wisdom without automatic foreclosure**.

## Recipient projection

The same canonical skill may need different explanatory projections for different ages, contexts, or levels of expertise.

For example, one stewardship principle might render as:

```text
child:       take care of what you own
teenager:    ownership includes maintenance cost and responsibility
adult:       evaluate total cost of ownership and opportunity cost
```

The projection may change explanation, examples, pacing, or interface.

It must not silently change the canonical principle, provenance, or authority state.

## Privacy and trust boundary

Longitudinal conversation is unusually sensitive source material.

A future skill-mining workflow should prefer:

- deriving a bounded candidate without copying unnecessary private source;
- explicit user review before promotion;
- explicit recipient / sharing scope;
- revocation and supersession;
- preserving reasons without exposing unrelated private conversations;
- summaries or evidence references over wholesale transcript transfer when possible.

Inheritance should not imply unrestricted surveillance access to the source person's complete history.

## Skills and external capabilities are different

A skill describes **how to approach a problem**.

A plugin, connector, API, tool, or other capability describes **what the system can access or do**.

```text
skill
!= plugin
!= permission
!= authority
```

A skill may request an external capability, but capability access must remain independently authorized and replaceable.

## Relationship to adjacent repositories

This future boundary composes with, but does not transfer ownership to:

- **agent-skills** — reusable process-skill packaging, provenance, and evaluation discipline;
- **Telos** — human-governed intent, authority, adoption, amendment, and succession;
- **Memory Lab** — epistemic-continuity tests such as inheritance without foreclosure;
- **TRACE** — provenance and ratification discipline for consequential human+agent work;
- **MASI Research** — eventual testing of whether stable bundles of bounded skills reveal responsibilities that justify purpose-built specialized intelligence;
- **YurrMom.com** — a possible public/horizontal distribution surface for intentionally published practical household systems and their derived executable projections.

These are architectural relationships, not claims that those repositories currently implement this pipeline.

## What would justify implementation

Do not build an inheritance runtime merely because the concept is attractive.

A first implementation should answer narrower questions such as:

1. Can a recurring pattern be proposed without treating frequency as validity?
2. Can a user inspect the exact reasons a candidate skill was inferred?
3. Can the user reject, revise, or ratify it without rewriting source history?
4. Can the skill be projected to another recipient without exposing unrelated source material?
5. Can later evidence narrow or supersede the skill while preserving ancestry?
6. Can external tools/plugins remain replaceable and independently authorized?

Until those questions are pressure-tested, this remains a future framework direction rather than a runtime commitment.
