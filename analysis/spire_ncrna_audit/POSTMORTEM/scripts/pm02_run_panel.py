"""pm02 — run the FROZEN Round-2 runner (unchanged file) on the panel. Only the member table it reads for
coding_frac is extended with panel members, in memory; r02_discover.py itself is not modified."""
import sys
from multiprocessing import Pool
from pathlib import Path
import pandas as pd

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE.parent / 'ROUND2/scripts'))
import r02_discover as r02  # noqa: E402

r02.MEM = pd.concat([r02.MEM, pd.read_csv(HERE / 'tables/PANEL_MEMBERS.tsv', sep='\t')], ignore_index=True)

if __name__ == '__main__':
    jobs = pd.read_csv(HERE / 'tables/JOBS_PANEL.tsv', sep='\t')
    with Pool(44) as p:
        res = p.map(r02.run, list(zip(jobs.gid, jobs.fasta_key, jobs.span)), chunksize=1)
    pd.DataFrame([s for sp, _ in res for s in sp]).to_csv(r02.SCRATCH / 'r2/panel_spans.tsv', sep='\t', index=False)
    Mo = pd.DataFrame([m for _, ms in res for m in ms])
    Mo.to_csv(r02.SCRATCH / 'r2/panel_motifs.tsv', sep='\t', index=False)
    print(Mo.groupby('status').size().to_string())
