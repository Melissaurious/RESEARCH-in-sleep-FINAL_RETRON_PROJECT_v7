RECONSTRUCTED by agent_v4 (2026-09-18) -- NOT the original V4 files (originals out/*_occ50.afa were never kept).
Commands (mafft v7.525, /home/borg/miniconda3/envs/retron_tradicional/bin):
  mafft --auto --thread 8 V4/.../cache/mestre_<frame>.faa > <frame>.auto.afa   (MAFFT chose FFT-NS-2 for all four)
  mafft --retree 2 --maxiterate 1000 --thread 8 V4/.../cache/mestre_ours.faa > ours.fftnsi.afa
  occupancy filter: keep columns where fraction of non-gap residues >= 0.50 (same count at > 0.50)
Match to V4 .iqtree (sites / constant / parsimony-informative / distinct patterns / 20 empirical aa freqs at 4 dp):
  ours, toro, wide, narrow: ALL MATCH EXACTLY -> these are almost certainly the alignments V4 used.
  fftnsi: 291 vs 290 sites, 289 vs 288 PI, 6/20 freqs exact -> NOT the V4 alignment (iterative refinement not reproduced).
  linsi: not attempted (L-INS-i on 1843 seqs is multi-hour).
