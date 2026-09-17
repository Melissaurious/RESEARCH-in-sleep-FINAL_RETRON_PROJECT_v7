# g7 — structures as an orthogonal interpretation layer. PLAN ONLY. Nothing here runs in g4b.

`rt07_g7_structural_and_published_comparators`. Follows g5 and g6.

## The rule that defines this gate

**Experimental structures were deliberately NOT used to derive the mapper.** The frozen
sequence coordinate system — `GII.deriv.hmm` under `hhmake -M 50`, its 150 anchors, and
`CAT_STATE` 262 — was built from sequence alone, precisely so that structure remains an
*independent* test rather than a circular one.

g7 may **constrain or test** the sequence-defined frame. It may **not** redefine it, and it
may not manufacture the seven-way partition that sequence evidence did not support
(launcher §"independent structural").

Structural data are not used in g4b, g5 or g6.

---

## Structure inventory and independence status — recorded now for later use

### Locally available: 25 structures

`/home/borg/RESEARCH-in-sleep-RETRON-DB_V3/MELISSA_DATA/crystal_structures/`, registered in
the launcher as `RE-DERIVE` (boundaries previously extracted; re-derive, do not inherit).

`24NC` `5G2X` `5HHJ` `5HHK` `5HHL` `5VBS` `6AR1` `6ME0` `6MEC` `7UIN` `7V9U` `7V9X` `7XJG`
`8FLI` `8QBM` `8UBD` `9C0I` `9D5X` `9E8Z` `9NNB` `9VHE` `9WY8` `9X94` `9YFD` `9Z6Z`

Also present and **not to be inherited**: `reference_boundaries.{json,py,tsv}`,
`boundary_extraction_report.txt` — prior extractions, re-derived in g7.

`6AR1` is the group II intron RT structure and is the natural first crosswalk target, since
the production profile is GII-derived.

### Independence status — the part that must not be forgotten

| structure set | independence from the mapper | note |
|---|---|---|
| the 25 local crystal structures | **not yet established** — must be measured in g7 | the mapper's construction sequences came from the myRT `RTs-collection.faa`; overlap must be measured before any structure is called an independent test |
| `anchors72` PDB members (`26CZ` `6AR1` `8BGJ` `8OZ7` `9I2F` `9LJE` `9WY8` `9Z6Z`) | **NOT independent** | g3 measured 100 % seed membership for `anchors72`; only 26 of 72 have a structure at all, the other 46 are sequence-propagated |
| His6-tagged entries (`26CZ` `6AR1` `8BGJ` `8OZ7` `9LJE` `9WY8` `9Z6Z`) | usable, **with the tag offset removed** | residue numbering from a tagged construct is offset by the tag length; a boundary read off it is shifted unless corrected. g3 flagged this explicitly |
| non-LTR R2-type RT structure | `DO-NOT-USE` until acquired | absent locally; needs network, under the predeclared governed-acquisition rule |
| `foldseek` | `DO-NOT-USE` until pinned | three local installs, no agreed semantic version; one must be pinned before any structural comparison |

**First action in g7, before any interpretation:** measure sequence overlap between each
structure's protein and the mapper's construction population, and classify each structure
`INDEPENDENT` / `NOT_INDEPENDENT` / `UNRESOLVED` under an explicitly registered rule. A
structure that is not independent is a crosswalk illustration, not a test.

---

## Questions g7 may ask

1. **Where do the frozen mapped states sit in solved RT structures?** Map `state_id` →
   residue in each structure's own sequence with the production mapper, then read the
   structural position. Reports agreement and disagreement, both.
2. **Correspondence to fingers / palm / thumb.** Against DSSP secondary structure, per
   structure. The launcher requires two predeclared gates first: whether a structural
   negative at the N-terminus is admissible, and whether two secondary-structure algorithms
   agree closely enough to set a boundary. Both are declared before running.
3. **Catalytic geometry.** Does `CAT_STATE` 262 land on the structurally identified
   catalytic aspartates? This is the sharpest available independent test of the one
   operational coordinate the mapper commits to — and it is a *test*, whose failure is
   reported, not repaired.
4. **Structural position of family-specific insertions.** Where the g6 insertion runs sit
   relative to the structural core.
5. **The historical RT0–RT7 crosswalk.** See below.

## The RT0–RT7 bridge — the one measurement that can resolve the crosswalk

`control/CROSSWALK_RT0_RT7.tsv` is `UNRESOLVED` in every row because nothing has measured
*production state → prior frame*. The registered recipe:

1. Take the prior frame `RT17_CORE` / `B_span17` (LENG 305, sha256 `f3ddb0b5…`) and its
   landed landmark points (RT1 42, RT2 87, RT3 146, RT4 193, RT5 229, RT6 263, RT7 276) and
   their LtrA P0A3U0 residues (49, 102, 160, 213, 308, 344, 357) from
   `g3_prior_region_correspondence.tsv`.
2. Run the **production mapper** on the LtrA protein sequence to obtain
   *production `state_id` → LtrA residue*.
3. Compose the two to get *production state ↔ prior-frame landmark*, and record the
   cardinality explicitly: `1:1` / `1:many` / `many:1` / `none` / `UNRESOLVED`.
4. Resolve a crosswalk row **only** where the composition is supported. Everything else
   stays `UNRESOLVED`.

Constraints this bridge inherits and cannot escape (from `g3_handoff_to_g4.tsv`):

* RT5 and RT6 collapse onto a single reconstructed g2 region — **no seven-way partition**;
* RT0 is `OBJECT_MISMATCH` and **no RT0 occupancy may be reported**;
* RT1 is the unstable landmark, moves between prior frames, and maps into the Blocker RT0
  zone on LtrA — a declared uncertainty;
* 24 of the prior frame's 29 blocks were placed by interpolating order between only 4
  motif-anchored blocks.

So a fully executed bridge still cannot return seven clean labels. That is a result, not a
shortfall.

## What g7 must not do

* Redefine the frozen sequence coordinate system, the anchors, `CAT_STATE`, or any threshold.
* Use structure to manufacture the seven-way partition.
* Inherit the prior `reference_boundaries` extraction instead of re-deriving it.
* Read residue numbering off a tagged construct without removing the tag offset.
* Treat a non-independent structure as an independent test.
* Use `foldseek` before one build is pinned, or the R2-type structure before governed
  acquisition.
