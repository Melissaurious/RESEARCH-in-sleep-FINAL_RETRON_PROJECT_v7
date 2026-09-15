# VIEWS — declared queries over the Stage-1 canonical tables

A view is a **query**, never a copied subset. Every downstream number names the view it was
computed on and the eligibility rule it applied. Tables live in `data/derived/` and are
registered with hashes in `data/README.md`; `pull.py` in this bundle runs the views.

Population contract: `docs/decisions/2026-09-15_stage1_population_rules.md`. The ncRNA-anchored
records are outside every view below.

## Grain views

| view | rule | unit | honest for | NOT honest for |
|---|---|---|---|---|
| `V-REC` | every row of `rt_records_v1` | raw record | provenance, per-file/per-database composition of the corpus as mined | any biological rate — it double-counts loci mined twice |
| `V-REC-DISTINCT` | `is_first_copy` | distinct raw record | the same, minus byte-identical duplicate lines | as above |
| `V-LOC` | distinct `locus_key` | genomic locus (contig spelling as given) | per-locus architecture, contig context | counts a RefSeq/GenBank twin as two loci |
| `V-LOC-PHYS` | distinct `physical_locus_key` | physical locus (`NZ_` normalised) | locus counts corrected for twin publication | collapsing is only *supported* where `collapse_supported` is true |
| `V-RT` | distinct `rt_seq_hash` | exact RT protein | sequence-level diversity, family composition of proteins | genomic frequency — one protein can sit at many loci |
| `V-RT-TAXOCC` | distinct `(rt_seq_hash, genome_id_norm)` | RT taxonomic occurrence | taxonomic spread of a protein | sequence diversity |
| `V-WIN` | distinct `window_dna_sha256` (empty excluded) | extracted window | identical-context detection (asymmetric: equal hash ⇒ equal context; unequal proves nothing) | context *difference* |
| `V-NCRNA-CALL` | every row of `rt_ncrna_calls_v1` | ncRNA call | call-level QC, model composition | pair counting (a call is not a pair) |
| `V-PAIR-PLACEMENT` | `(locus, RT, ncRNA call)` | one placement | geometry as observed | deduplicated biology |
| `V-PAIR-KEY` | distinct `(rt_seq_hash, nc_seq_hash)` | exact RT–ncRNA pair | pair-level association | placement frequency |

## Eligibility predicates (flags, not filters)

| predicate | keeps | removes (reported as a denominator effect) |
|---|---|---|
| `elig_exact_rt` | well-formed RT protein | empty, internal-stop or non-amino-acid sequences |
| `elig_rt_coords` | RT interval verified against window DNA by back-translation | unverified: RT outside/partly outside the window, inverted window, mismatch, opposite strand |
| `elig_geometry` | `elig_rt_coords` **and** a self-consistent window | as above, plus window-length inconsistency |
| `elig_rt_length` | a usable amino-acid length | same as `elig_exact_rt` |
| `elig_rt_completeness` | verified coordinates plus a Prodigal partial flag or derivable codons | as `elig_rt_coords` |

`MULTI` is a stratum, never merged into a single family: filter on `file_label == "MULTI"` or
`multilabel`. A multi-label record inside a single-family file carries `multilabel == True` and
must not be counted in two single-family denominators.

## Standard pulls

```
python pull.py --view V-RT --family Retron --elig elig_exact_rt --out rt.tsv
python pull.py --view V-LOC-PHYS --database gtdb_bacteria --elig elig_geometry --count
python pull.py --view V-PAIR-PLACEMENT --with-ncrna --elig elig_geometry --out pairs.tsv
python pull.py --view V-REC --record-key master_Retron_merged_oriented.jsonl:12345 --raw
```

`--raw` re-reads the original JSON line by `(source_file, byte_offset, byte_len)` from the
pinned corpus, so any field dropped from the derived tables is still one command away.
