# PROJECT ANALYSIS PRINCIPLES

**Project:** Retron / Reverse-Transcriptase PhD project
**Purpose:** Reusable scientific and analytical principles for future launchers, analyses, validation tasks, and downstream interpretation.

This document records methodological lessons learned during development and validation of the Stage-2 RT conserved-state mapper.

It is not a replacement for task-specific launchers.

Its purpose is to prevent repeated methodological churn, hidden circularity, weak validation, unnecessary over-engineering, and loss of project momentum.

---

# 1. Start with the scientific question, not the inherited method

For every new task, state first:

1. What biological/scientific question are we asking?
2. What quantity would answer it?
3. Is that quantity actually observable with the available data?
4. What downstream decision or analysis will this unlock?

Do not begin from:

* an old script;
* an existing HMM;
* an inherited classification;
* a previously generated table;
* a convenient benchmark;
* or a method we happen to know how to run.

Methods are instruments for answering questions, not the project objective.

---

# 2. Define the estimand before selecting the method

Before implementation, distinguish:

* what we want to know;
* what we can measure directly;
* what we can estimate indirectly;
* what remains unidentifiable.

Use explicit categories where useful:

`ESTABLISHABLE`

`PARTIALLY_ESTABLISHABLE`

`UNESTABLISHED`

Do not manufacture “ground truth” merely because an operational proxy exists.

Examples from Stage 2:

* exact biological RT-region boundaries were not independently observable;
* conserved homologous state correspondence was observable;
* sequence-state callability was observable;
* residue-level biological accuracy against an independent coordinate truth set remained unestablished.

The analysis must follow the identifiable question.

---

# 3. Separate historical meaning from operational measurement

Historical nomenclature, previous classifications and published conventions may be scientifically important without being suitable as operational ground truth.

For example:

* historical RT0–RT7 labels remain useful as a historical crosswalk;
* they should not automatically become output classes for a modern sequence mapper.

Always distinguish:

`HISTORICAL / INTERPRETIVE FRAME`

from:

`OPERATIONAL MEASUREMENT FRAME`.

Do not force one to become the other.

---

# 4. Assign every dataset a role before analysis

Before executing a method, classify every important data source as one or more of:

* `DERIVATION`
* `DEVELOPMENT`
* `CHALLENGE / HOLDOUT`
* `COMPARATOR`
* `STRUCTURAL COMPARATOR`
* `METADATA / STRATIFICATION`
* `DOWNSTREAM APPLICATION POPULATION`

Do not allow roles to drift silently.

If a holdout is inspected and subsequently influences:

* thresholds;
* rules;
* feature selection;
* architecture;
* parameter choices;

it has become development data.

Record that explicitly.

Never continue calling it independent validation.

---

# 5. Treat old work as evidence, not authority

Previous work can provide:

* candidate ideas;
* known failure modes;
* useful sequences;
* comparison points;
* historical context;
* possible thresholds;
* candidate controls.

It should not automatically define the new analysis.

Use a three-level reuse classification.

## GREEN — safe to reuse directly

Examples:

* raw/canonical sequence data;
* primary-source metadata;
* independently reproduced utilities;
* verified immutable derived datasets;
* primary literature evidence.

## AMBER — inspect before reuse

Examples:

* old scripts;
* alignments;
* thresholds;
* HMMs;
* curated labels;
* previous models;
* intermediate derived tables.

## RED — do not inherit as truth

Examples:

* circular “gold” sets;
* validation sets overlapping derivation;
* unverifiable historical outputs;
* manually interpolated coordinates presented as biological truth;
* datasets whose provenance cannot be reconstructed;
* claims whose denominator or measurement logic is unclear.

Default future strategy:

> plan cleanly first; inspect old work second for useful refinements.

Do not design the new task around old machinery merely because it exists.

---

# 6. Full data should remain observable until the analysis justifies trimming

Do not pre-delete the sequence/data space in which the biological question may live.

Stage-2 example:

Pfam/myRT RVT_1 fragments removed substantial N-terminal sequence, making N-terminal architecture impossible to test from those fragments alone.

General rule:

> preserve complete/raw objects as the observational substrate; trim or mask only after the relevant correspondence or exclusion has been justified.

Maintain reversible coordinate transforms whenever trimming/masking is necessary.

---

# 7. Measure independence directly

Do not infer independence from:

* family labels;
* cluster IDs;
* different filenames;
* different tools;
* different databases;
* or “held-out” naming.

If independence matters, measure it.

Examples:

* direct pairwise identity;
* bidirectional coverage;
* exact overlap;
* genealogy/provenance overlap;
* shared seeds;
* shared models;
* shared derivation objects.

A cluster split is not automatically an independent split.

A different family label is not automatically an independent lineage.

---

# 8. Prevent circular validation

Ask for every validation result:

> Could the object being used as validation have influenced the method being validated?

Common circularity sources:

* labels produced by the same tool family used in derivation;
* HMM seeds reused in challenge sets;
* structures used both to define and “validate” coordinates;
* thresholds chosen after inspecting the final holdout;
* catalogue labels inherited from the classifier being evaluated.

If overlap exists, the result may still be useful, but label it appropriately:

* self-consistency;
* development performance;
* related-family transfer;
* comparator agreement;

not independent validation.

---

# 9. Predeclare only what matters

Predeclaration is most valuable for choices that can materially change the conclusion.

Prioritize predeclaring:

* primary estimands;
* holdout selection;
* success/failure criteria;
* important thresholds;
* negative controls;
* key denominators;
* stopping rules.

Do not overload every exploratory task with unnecessary formalism.

Exploration is allowed.

The distinction should be explicit:

`EXPLORATORY`

versus

`CONFIRMATORY`.

---

# 10. Confirmatory holdouts are consumable resources

A final holdout should normally be used once.

After opening it:

* do not tune thresholds against it;
* do not modify criteria because it failed;
* do not select a replacement family because another might perform better.

If a holdout influences method development, demote it to development data and acquire a genuinely fresh holdout if one is essential.

Avoid serially testing holdouts until one passes.

---

# 11. Every important inferential method should have controls

Where scientifically meaningful, consider three categories.

## Positive control

Something expected to succeed.

Purpose:

* verify the method can recover known/expected signal.

## Negative control

Something expected not to contain the target signal.

Purpose:

* estimate false correspondence / background behavior.

Examples:

* composition-preserving shuffles;
* appropriate unrelated data;
* scrambled controls.

## Failure control

An intentionally malformed or adverse case that demonstrates the test can actually fail.

Purpose:

* prevent vacuous tests.

A test that always returns PASS is not evidence.

Not every table needs all three controls.

Every load-bearing inferential method should explicitly ask whether each control class is appropriate.

---

# 12. Controls must preserve the relevant nuisance structure

A negative control is useful only if it tests the intended null.

Ask:

* what properties does the real data possess?
* which should the null preserve?
* which should it destroy?

Examples:

* monomer composition;
* dipeptide frequencies;
* sequence length;
* local composition;
* genealogy;
* alignment geometry.

Do not treat an obviously weak null as strong evidence merely because separation is large.

Report control classes separately when pooled summaries can conceal a difficult control.

---

# 13. Tests must be capable of failure

For every important automated test, ask:

1. What input should make this PASS?
2. What input should make this FAIL?
3. Has both behavior been demonstrated?

Classify tests as:

`FALSIFIABLE_EMPIRICAL_TEST`

or

`IMPLEMENTATION_INVARIANT`.

Implementation invariants can verify software correctness.

They must not be presented as biological evidence.

---

# 14. Do not confuse algorithmic guarantees with empirical findings

If an algorithm guarantees:

* monotonic alignment order;
* one-to-one coordinate ordering;
* colinearity;
* conservation of an input constraint;

those properties cannot independently validate biological correspondence.

Ask whether the result could have been different under the same algorithm.

If not, it is an implementation property.

---

# 15. Presence, non-detection and absence are different states

Do not translate mapping failure directly into biological absence.

Prefer explicit states such as:

* `PRESENT / MAPPED`
* `AMBIGUOUS`
* `UNSUPPORTED`
* `DELETED_STATE`
* `NOT_DETECTED_INSPECTABLE`
* `UNINSPECTABLE`
* `OUTSIDE_SCOPE`
* `TOOL_FAILURE`

A biological “absence” claim requires additional evidence that:

* the relevant region was inspectable;
* the method has demonstrated power in the appropriate sequence regime;
* divergence is not a plausible explanation;
* the result is reproducible under reasonable perturbations.

---

# 16. Denominators are part of the scientific claim

Every reported percentage must define its denominator.

Prefer tables that store:

`numerator`

`denominator`

`fraction`

rather than fraction alone.

Watch for denominator changes between:

* complete sequence length;
* aligned region;
* HMM match states;
* callable states;
* inspectable sequences;
* family consensus positions.

Never compare percentages with different denominators without making the distinction explicit.

---

# 17. Thresholds must not emerge accidentally from the result

Avoid:

* selecting the first convenient grid value;
* choosing a cutoff because it happens to separate the holdout;
* declaring a threshold “minimal” when unsampled intermediate values exist.

Prefer:

* biological/statistical justification;
* construction-only calibration;
* sensitivity analysis;
* continuous reporting when no meaningful cutoff exists.

If a threshold is implementation-specific, say so.

---

# 18. Sensitivity analysis should test load-bearing assumptions

Do not sensitivity-test everything.

Prioritize assumptions that could change the scientific interpretation.

Examples:

* alignment match-state definition;
* sequence identity threshold;
* clustering rule;
* negative-control construction;
* mapping support threshold.

If an interpretation disappears under a reasonable alternate implementation, narrow the claim rather than hiding the sensitivity.

Stage-2 example:

the family-symmetric shared-core claim was withdrawn because it was not robust under `-M a2m`.

---

# 19. Independent review should be adversarial but tiered

Do not spend the strongest independent reviewer on trivial implementation defects.

Recommended workflow:

### Layer 1 — deterministic/self checks

* counts;
* schemas;
* file integrity;
* reproducibility;
* unit tests;
* obvious invariants.

### Layer 2 — inexpensive independent preflight

Use a separate model/tool where available to inspect:

* code defects;
* stale values;
* unchecked branches;
* fail-open logic;
* provenance inconsistencies;
* malformed-input handling;
* unused variables;
* path/environment dependence.

This may use a cheaper independent model such as Gemini if permitted by governance.

### Layer 3 — formal adversarial review

Reserve Codex / strongest independent reviewer for:

* identifiability;
* leakage;
* circularity;
* statistics;
* falsifiability;
* independence;
* confirmatory claims;
* whether a gate may advance.

Do not ask formal reviewers to endlessly optimize already adequate engineering.

---

# 20. Review findings must be classified

Every reviewer suggestion should be assigned to:

* `REQUIRED / LOAD-BEARING`
* `OPTIONAL / STRENGTHENING`
* `OUT-OF-SCOPE RESIDUAL RISK`

Do not automatically implement every reviewer suggestion.

A defect is load-bearing if it can materially alter:

* the scientific measurement;
* holdout independence;
* mapper interpretation;
* reproducibility;
* confirmatory outcome.

Optional robustness improvements should not indefinitely block progress.

---

# 21. Adversarial robustness is bounded by the declared input model

A validator can always be attacked with increasingly exotic artificial inputs.

The relevant question is:

> Can this failure occur through the registered pipeline?

A theoretically constructible failure that requires an unreachable hostile object may be documented as residual engineering risk rather than allowed to create an infinite hardening cycle.

Define the input contract clearly.

Test all reachable malformed cases.

Do not attempt to build a security-hardened general-purpose validator unless that is actually the project objective.

---

# 22. Freeze means immutable

Once a bundle is submitted for review:

* do not edit it;
* do not add commentary;
* do not create bytecode inside it;
* do not repair it;
* do not regenerate it.

Post-freeze observations belong outside the reviewed bundle.

Freeze integrity should detect:

* additions;
* deletions;
* modifications;
* renames;
* symlinks;
* generated bytecode where prohibited.

The root of trust must not live entirely inside the artifact it authenticates.

---

# 23. Reproducibility must be independent of expected outputs

A valid verifier should:

1. authenticate registered inputs;
2. reproduce into a clean temporary directory;
3. compare against frozen canonical outputs;
4. fail non-zero on drift;
5. never regenerate expected outputs before comparing them.

Canonical outputs should avoid environment-specific paths unless they are intentionally excluded from deterministic comparison.

---

# 24. Preserve failed analyses as evidence

Do not erase:

* failed gates;
* false starts;
* invalid controls;
* superseded methods;
* reviewer-refuted claims.

Record them clearly and mark them non-canonical.

They are useful because they prevent future repetition of the same mistakes.

Do not rehabilitate broken historical bundles merely to make the archive look clean.

---

# 25. When the infrastructure becomes the problem, rebuild cleanly once

If repeated defects arise in:

* manifests;
* verifier logic;
* freeze machinery;
* packaging;
* provenance plumbing;

while the scientific object remains stable:

stop patching historical artifacts one defect at a time.

Instead:

1. preserve historical bundles as audit evidence;
2. build one minimal clean artifact from registered inputs;
3. include all known controls prospectively;
4. freeze it;
5. review it once.

Do not confuse validation-infrastructure perfection with scientific progress.

---

# 26. Narrow failed broad claims instead of endlessly redesigning

If evidence does not support:

`UNIVERSAL`

ask whether it supports:

`BROAD`

`LINEAGE-LEVEL`

`FAMILY-LEVEL`

or

`CONSTRUCTION-SCOPED`.

A narrower defensible claim is a valid scientific result.

Do not repeatedly redesign the method merely to recover the original ambitious wording.

---

# 27. Predefine a stopping condition before starting a gate

Every launcher should answer:

> What result lets us stop?

and:

> What downstream action does this gate unlock?

Examples:

* PASS → proceed;
* FAIL → narrow the claim;
* ambiguous → one bounded repair;
* final holdout → terminal decision.

Avoid open-ended loops such as:

> try another method / family / threshold until something works.

---

# 28. One bounded repair cycle should remain bounded

If a reviewer identifies an implementation defect:

repair the defect.

Do not automatically:

* introduce a new method;
* add a new holdout;
* broaden the dataset;
* revisit every previous assumption.

If the underlying scientific object survives, preserve it.

---

# 29. Completion beats unnecessary perfection

A task is finished when it has enough evidence to support the **narrow claim needed downstream**.

It is not finished only when every conceivable criticism has been eliminated.

Before authorizing further work, ask:

> Could this change the scientific conclusion or downstream decision?

If no:

classify it as optional unless required for reproducibility or integrity.

Project completion is itself a scientific constraint.

---

# 30. Every task should produce downstream value

Prefer analyses that produce at least one of:

* a thesis figure;
* a thesis table;
* a database annotation;
* a reusable method;
* a downstream dataset;
* a biological conclusion;
* an experiment-selection criterion;
* a publication-ready result.

If methodological work does not unlock downstream science, reconsider its priority.

---

# 31. Large-scale application comes after instrument freeze

Do not use the full catalogue as development data unless that is explicitly the study design.

For this project:

the ~501k exact RT catalogue is primarily a downstream application population.

Develop and validate the instrument first.

Then apply it broadly.

This preserves interpretability and prevents accidental large-scale tuning.

---

# 32. Existing tool annotations are metadata unless independently validated

MyRT, PADLOC and DefenseFinder outputs are highly useful.

Use them for:

* stratification;
* sampling;
* system context;
* robustness analyses;
* disagreement analyses;
* family/context metadata.

Do not treat agreement with them as independent validation when the new analysis shares their models, seeds, rules or genealogy.

Phrase downstream results conditionally, for example:

> Among sequences classified by MyRT as family F...

rather than:

> MyRT proves that these sequences are biologically family F.

---

# 33. Structural data should remain orthogonal when possible

Experimental structures are especially valuable when they were not used to define the sequence coordinate system.

Use structures later to ask:

* whether mapped states occupy homologous structural positions;
* whether catalytic geometry agrees;
* how insertions/extensions map structurally;
* how operational states correspond to fingers/palm/thumb;
* how historical RT0–RT7 relates to structure.

Avoid using the same structure to define and independently validate the same coordinate feature.

---

# 34. Keep exploration and confirmation separate

Exploration may be flexible.

Confirmation must be frozen.

A healthy workflow is:

`exploration`
→
`method definition`
→
`preflight`
→
`freeze`
→
`confirmatory holdout`
→
`interpretation`.

Do not loop from confirmatory outcomes back into method tuning while still calling the result confirmatory.

---

# 35. Audit mistakes explicitly

When an error is discovered, record:

* expected;
* observed;
* when detected;
* scientific effect;
* repair;
* whether previous results are invalidated.

Do not silently overwrite mistakes.

A transparent error trail is more credible than an artificially clean history.

---

# 36. Avoid overclaiming from successful tests

A passed experiment supports only the tested scope.

One-family transfer does not establish universality.

One structural example does not establish architectural invariance.

A successful computational mapping does not establish biological function.

Always state:

* tested population;
* tested implementation;
* relevant denominator;
* remaining untested scope.

---

# 37. Default workflow for future launchers

For future tasks, prefer the following sequence:

### Phase 1 — Scientific framing

* question;
* estimand;
* observability;
* downstream value;
* stop condition.

### Phase 2 — Data-role audit

* derivation;
* development;
* challenge;
* comparators;
* metadata;
* leakage/genealogy.

### Phase 3 — Small falsification pilot

* minimal data;
* positive/negative/failure controls;
* determine whether the basic premise survives.

### Phase 4 — Method freeze

* parameters;
* thresholds;
* success/failure criteria;
* holdout.

### Phase 5 — Cheap preflight review

* code;
* accounting;
* provenance;
* reproducibility;
* fail-open behavior.

### Phase 6 — Independent adversarial review

Only load-bearing scientific issues.

### Phase 7 — Confirmatory execution

Single-shot where appropriate.

### Phase 8 — Downstream application

Scale only after the instrument/claim is frozen.

---

# 38. Launcher questions that should always be answered

Every future launcher should explicitly answer:

1. What is the biological question?
2. What is the primary estimand?
3. What is actually observable?
4. What datasets are derivation/development/challenge/comparator?
5. What could create circularity?
6. What are the positive controls?
7. What are the negative controls?
8. What demonstrates the method can fail?
9. What assumptions are load-bearing?
10. What needs sensitivity analysis?
11. What is the holdout, if any?
12. What outcome counts as success?
13. What outcome counts as a useful negative result?
14. What result lets us stop?
15. What downstream task does this unlock?
16. Which outputs should become thesis/database artifacts?
17. What old work is Green/Amber/Red for reuse?
18. What should the independent reviewer attack?
19. What reviewer findings are allowed to block progression?
20. When do we narrow the claim instead of redesigning?

---

# 39. Project-level principle

The project should optimize for:

> **credible biological insight per unit of research effort**

—not maximum methodological complexity.

Scientific rigor and project completion are not opposing goals.

Good scope control is part of rigor.

A narrower result that is reproducible, falsifiable and interpretable is preferable to a broader claim that requires endless tuning and validation.

---

# 40. Stage-2 lesson in one sentence

The Stage-2 experience should be remembered as:

> Start from the observable scientific question, derive the minimum defensible instrument, test whether it can fail, validate it on truly independent data, narrow the claim when necessary, and stop once the result is sufficient to unlock downstream biology.
