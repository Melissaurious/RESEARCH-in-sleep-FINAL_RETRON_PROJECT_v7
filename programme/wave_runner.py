#!/usr/bin/env python3
"""Thin autonomous wave coordinator. No scientific decisions live here."""
from __future__ import annotations
import argparse, csv, fcntl, hashlib, json, os, shlex, subprocess, sys, time
from datetime import datetime, timezone
from pathlib import Path
from autonomy_state import TERMINAL, ScheduleTask, acceptance_verdict, atomic_write, choose_launchable, executor_terminal_state, load_execution_spec, normalise_prepare_result, parse_front_matter, read_tsv, self_checks_all_pass, sha256_file, upsert_tsv, validate_type_a_execution, write_tsv
from resource_broker import Broker

SYN=Path(__file__).resolve().parents[1]; P=SYN/'programme'; BOARD=P/'TASK_BOARD.tsv'; LEDGER=P/'EXECUTION_LEDGER.tsv'; EXEC=P/'executions'; WORKER=P/'task_worker.py'; LIMITS=P/'RESOURCE_LIMITS.tsv'
LEDGER_FIELDS=['task_id','question_short','freeze_commit','execution_commit','state','population','endpoint','backend','primary_output','task_report','interpretation_ceiling','started_at','finished_at']
STATUS_FIELDS=['task_id','state','detail','freeze_commit','worker_pid','analysis_pid','slurm_job_id','started_at','finished_at']
# TERMINAL is imported from autonomy_state so the acceptance boundary has ONE definition.
ARIS_RUN_STATE=Path('/home/borg/aris_repo/tools/run_state.py')

def utc(): return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00','Z')
def run(cmd,cwd=SYN,check=True):
    p=subprocess.run(cmd,cwd=cwd,text=True,capture_output=True)
    if check and p.returncode: raise RuntimeError(f"{' '.join(cmd)}: {p.stderr.strip()}")
    return p
def git(*a,cwd=SYN,check=True): return run(['git',*a],cwd,check).stdout.strip()
def split(v): return tuple(x.strip() for x in (v or '').split(';') if x.strip() and x.strip()!='-')
def rows(path): return read_tsv(path)[1]
def board(): return {r['task_id']:r for r in rows(BOARD)}
def set_board(tid,state,note=''):
    fields,rr=read_tsv(BOARD)
    for r in rr:
        if r['task_id']==tid:
            r['state']=state; r['notes']=(r.get('notes','')+' | '+note).strip(' |') if note else r.get('notes',''); break
    else: raise RuntimeError(f'{tid} missing from TASK_BOARD.tsv')
    write_tsv(BOARD,fields,rr)
def ledger(tid,**u):
    r={k:'' for k in LEDGER_FIELDS}; r.update(task_id=tid,question_short=u.pop('question_short',tid)); r.update(u); upsert_tsv(LEDGER,'task_id',r,LEDGER_FIELDS)
def status_path(w): return w.parent/'WAVE_STATUS.tsv'
def load_status(w): return {r['task_id']:r for r in rows(status_path(w))} if status_path(w).exists() else {}
def save_status(w,s): write_tsv(status_path(w),STATUS_FIELDS,[s[k] for k in sorted(s)])
def set_status(w,s,tid,state,detail='',**kw):
    r=s.setdefault(tid,{k:'' for k in STATUS_FIELDS}); r.update(task_id=tid,state=state,detail=detail); r.update({k:str(v) for k,v in kw.items() if k in r}); save_status(w,s)
def commit(paths,msg):
    rel=[str(x.relative_to(SYN)) for x in paths if x.exists()]
    if not rel:return
    run(['git','add','--',*rel]);
    if git('diff','--cached','--name-only'): run(['git','commit','-m',msg])
def alive(pid):
    try: os.kill(pid,0); return pid>0
    except OSError:return False

def aris_run_id(w): return w.parent.name
def aris(*a):
    """Best-effort call into pinned ARIS tools/run_state.py.

    ARIS owns resumable run state; this layer mirrors EXECUTOR statuses into it so a
    resume resolves against ARIS rather than against a second state system.  It is
    deliberately non-fatal: ARIS being unavailable must not kill a detached wave, and
    WAVE_STATUS.tsv remains the generated operator view either way.
    """
    if not ARIS_RUN_STATE.exists(): return None
    return run([sys.executable,str(ARIS_RUN_STATE),*a],check=False)
def aris_start(w,task_ids):
    aris('start',str(SYN),aris_run_id(w),'--phases',','.join(task_ids))
def aris_set(w,tid,status,artifact=''):
    # Executor statuses only. A worker self-report can never reach `accept` from here.
    a=['set',str(SYN),aris_run_id(w),tid,status]
    if artifact: a+=['--artifact',artifact]
    aris(*a)
def aris_accept(w,tid,verdict_id,reviewer):
    # Permitted by ARIS only for a CROSS-MODEL reviewer or A DETERMINISTIC VERIFIER, and
    # only with a verdict id and a named reviewer. Reached solely from deterministic_accept().
    aris('accept',str(SYN),aris_run_id(w),tid,'--verdict-id',verdict_id,'--reviewer',reviewer)

DET_REVIEWER='deterministic-validator:autonomy_state.validate_type_a_execution'

#: Mechanical failures that say nothing about the science and are safe to retry verbatim.
#: ⛔ A failed scientific CONTROL is never in this list: a control failure is a result.
TRANSIENT_SIGNATURES=(
    'specs_exist.sh did not pass',        # D19: SIGPIPE + pipefail, ~5-10% of runs
    'Connection closed by remote host',
    'Connection timed out',
    'Temporary failure in name resolution',
    'sbatch: error: Batch job submission failed',
    'Socket timed out',
    'error: Unable to contact slurm controller',
)
MAX_TRANSIENT_RETRIES=3
#: Preparing, reviewing and repairing write text; they do not perform the task's I/O.
#: Charging them the execution budget starved the pool and blocked Ibex-bound work too.
AUTHORING_COST=1

def stale_base(tid):
    """True when the task worktree does NOT contain the current synthesis HEAD.

    Such a worktree cannot see a repo-level governance fix, because worktree() rebases
    only while preparing. T-A23d sat at ccb4832 while the fix lived at 623f2ce, so its
    copy of docs/BLOCKED.md still tripped specs_exist.sh on every launch.
    """
    fm=parse_front_matter(P/'tasks'/tid/'TASK_LAUNCHER.md') if (P/'tasks'/tid/'TASK_LAUNCHER.md').exists() else {}
    wt=Path(fm.get('worktree','')) if fm.get('worktree') else SYN.parent/f"{SYN.name.removesuffix('-synthesis')}-{tid}"
    if not wt.is_dir(): return False
    head=git('rev-parse','HEAD')
    return run(['git','merge-base','--is-ancestor',head,'HEAD'],cwd=wt,check=False).returncode!=0

def transient_reason(tid,w):
    """Return the transient signature that explains a launch failure, else ''."""
    log=w.parent/'runs'/f'{tid}.worker.log'
    if not log.exists(): return ''
    try: tail=log.read_text(errors='replace')[-4000:]
    except OSError: return ''
    return next((s for s in TRANSIENT_SIGNATURES if s in tail),'')

def deterministic_accept(tid,spec,w,st):
    """Type-A execution-validity acceptance. Returns (state,note) on success, else None.

    An ordinary preregistered computation must not need a semantic reviewer merely to
    establish that it ran validly, so a task whose frozen launcher declares
    `autonomy_tier: A` is promoted COMPLETE_AWAITING_REVIEW -> PASS when an INDEPENDENT
    deterministic re-validation passes. The worker's own claim is never the evidence.

    This certifies execution validity only. Whether the result supports a claim, and
    whether anything enters thesis/paper language, stay Type-B and stay with ARIS
    reviewer routing and the operator's human_input_audit.
    """
    try:
        wt=Path(spec['worktree']); out=wt/spec['output_directory']
        tier=parse_front_matter(wt/'programme'/'tasks'/tid/'TASK_LAUNCHER.md').get('autonomy_tier','').strip().upper()
        if tier!='A': return None
        ok,checks=validate_type_a_execution(spec,wt,out)
        rec=w.parent/'acceptance'; rec.mkdir(exist_ok=True)
        vid=acceptance_verdict(tid,spec['freeze_commit'],checks)
        atomic_write(rec/f'{tid}.acceptance.json',json.dumps(
            {'task_id':tid,'freeze_commit':spec['freeze_commit'],'verdict_id':vid,
             'reviewer':DET_REVIEWER,'acceptance_type':'TYPE_A_EXECUTION_VALIDITY',
             'accepted':ok,'checked_at':utc(),'checks':checks,
             'ceiling':'Execution validity only. Not a judgment that the interpretation is '
                       'justified or that any result may be promoted to a claim.'},
            indent=2,sort_keys=True)+'\n')
        if not ok:
            failed=[c['check'] for c in checks if c['result']=='FAIL']
            return ('COMPLETE_AWAITING_REVIEW',f'deterministic validation FAILED: {",".join(failed)}')
        aris_accept(w,tid,vid,DET_REVIEWER)
        return ('PASS',f'Type-A execution validity accepted deterministically; verdict {vid}')
    except Exception as e:
        return ('COMPLETE_AWAITING_REVIEW',f'deterministic validation error: {e}')
def limit(name,default=None):
    for r in rows(LIMITS):
        if r['resource']==name: return int(r['capacity'])
    if default is None: raise RuntimeError(f'{name} missing from RESOURCE_LIMITS.tsv')
    return default
def tokens(): return limit('NVME_TOKENS')

def make_broker():
    """One broker per coordinator. Enforces BOTH local NVMe/CPU/GPU and IBEX_SUBMISSIONS."""
    return Broker(nvme_capacity=limit('NVME_TOKENS'),
                  ibex_capacity=limit('IBEX_SUBMISSIONS',4),
                  cpu_capacity=limit('LOCAL_CPU_THREADS',44),
                  probe=os.environ.get('RETRON_BROKER_PROBE','1')!='0')
def lock():
    p=Path(git('rev-parse','--git-common-dir')).resolve()/'retron-autonomous-wave.lock'; f=p.open('w'); fcntl.flock(f.fileno(),fcntl.LOCK_EX|fcntl.LOCK_NB); f.write(f'pid={os.getpid()} {utc()}\n'); f.flush(); return f

def worktree(tid):
    fm=parse_front_matter(P/'tasks'/tid/'TASK_LAUNCHER.md'); wt=Path(fm.get('worktree','')) if fm.get('worktree') else SYN.parent/f"{SYN.name.removesuffix('-synthesis')}-{tid}"; br=f'task/{tid}'; base=git('rev-parse','HEAD')
    if wt.exists():
        if git('rev-parse','--abbrev-ref','HEAD',cwd=wt)!=br: raise RuntimeError(f'unsafe existing worktree {wt}: wrong branch')
        # A MODIFIED TRACKED file means the frozen/base state was altered -> refuse.
        # Untracked files under this task's own programme/tasks/<tid>/ are its prepare
        # output, which prepare rewrites and freeze commits; a previous abandoned prepare
        # must not make the worktree permanently unrestartable. Anything else untracked
        # is unexpected and still refused.
        if git('status','--porcelain','--untracked-files=no',cwd=wt): raise RuntimeError(f'unsafe existing worktree {wt}: tracked files modified')
        stray=[l[3:] for l in git('status','--porcelain',cwd=wt).splitlines() if l.startswith('??') and not l[3:].startswith(f'programme/tasks/{tid}/')]
        if stray: raise RuntimeError(f'unsafe existing worktree {wt}: unexpected untracked {stray[:3]}')
    else:
        exists=run(['git','show-ref','--verify','--quiet',f'refs/heads/{br}'],check=False).returncode==0
        run(['git','worktree','add',str(wt),br] if exists else ['git','worktree','add','-b',br,str(wt),base])
    if run(['git','merge-base','--is-ancestor',base,'HEAD'],cwd=wt,check=False).returncode:
        p=run(['git','rebase',base],cwd=wt,check=False)
        if p.returncode: run(['git','rebase','--abort'],cwd=wt,check=False); raise RuntimeError(f'rebase failed: {p.stderr.strip()}')
    return wt

def prepare_start(tid,row,wt):
    """Launch the preparation agent WITHOUT waiting for it. Returns (proc, log_paths)."""
    base=git('rev-parse','HEAD'); refs='\n'.join('  - '+x for x in split(row['design_refs']))
    prompt=f'''Prepare exactly task {tid} in {wt}. DO NOT run primary science. Read its TASK_LAUNCHER.md, {P/'WORKING_RULES.md'}, {SYN/'review-stage/TASK_PROTOCOL.md'}, and:\n{refs}\nCurrent authoritative project-synthesis base is {base}. Preserve approved science. Ordinary implementation choices are autonomous. If no substantive TASK_LAUNCHER.md exists yet, you MAY write one, but ONLY by converting an approved design packet listed above into a launcher: cite the packet and its section, read the prior work it names FIRST, and carry its population, denominator, inference unit, endpoints, controls (positive AND negative), success/falsification criterion, exposure/spend rules and interpretation ceiling across verbatim in substance. Declare autonomy_tier yourself. You are the AUTHOR, never the approver: an independent cross-model reviewer judges this launcher before it can be frozen, and it will be rejected if a control, a denominator or the ceiling is missing. ⛔ Never invent a scientific endpoint, threshold or population that the packet does not already fix -- if one is genuinely missing, write PREPARE_RESULT.json with status REVIEW_REQUIRED naming exactly what is undecided. If a genuinely new biological endpoint/threshold/population decision is needed, write programme/tasks/{tid}/PREPARE_RESULT.json with status REVIEW_REQUIRED and stop. Otherwise implement code+fixtures, run only self-checks, update launcher to base_commit={base}, base_branch=project-synthesis, state=AUTHORIZED, frozen=true; do not create primary output and do not commit. The launcher front matter MUST declare autonomy_tier: A for a preregistered computation whose acceptance gate is fully machine-verifiable (frozen hashes, input hashes, blocking controls, manifest, run log, report schema), or autonomy_tier: B if accepting it needs a human/cross-model judgment of merit or interpretation; tier A is then accepted by deterministic validation alone, tier B waits for semantic review. The implementation MUST write, into its declared output_directory, ALL THREE of: TASK_REPORT.md (containing the lines TASK_STATE: <PASS|VOID|STOP|INCONCLUSIVE|BLOCKED> and SCIENTIFIC_OUTCOME: <SUPPORTS_H1|SUPPORTS_H0|FALSIFIED|BOUND|DESCRIPTIVE|NOT_APPLICABLE>), logs/run_log.json, and OUTPUT_MANIFEST.sha256 covering every file it writes. A run that omits any of these is rejected as ARTIFACT_INVALID no matter how well the science went, so include a self_check asserting all three exist. Write PREPARE_RESULT.json schema_version=1, status=READY_TO_FREEZE, task_id, command argv, inputs(dataset_id,path,sha256), backend, resources(cpu_threads,memory_gb,io_tokens={row['io_tokens']}), runtime(max_runtime_seconds,resume_allowed,stop_note), self_checks, unresolved_decision.'''
    cmd=shlex.split(os.environ.get('RETRON_PREPARE_COMMAND','claude --dangerously-skip-permissions -p'))+[prompt]
    log=row['_wave'].parent/'prepare_logs'; log.mkdir(exist_ok=True); out=log/f'{tid}.stdout.log'; err=log/f'{tid}.stderr.log'
    o=out.open('w'); e=err.open('w')
    proc=subprocess.Popen(cmd,cwd=wt,stdout=o,stderr=e,text=True,start_new_session=True)
    return proc,(out,err)

def review_start(tid,wt,rnd):
    """Launch the INDEPENDENT adversarial reviewer (codex) without waiting.

    ⛔ The drafting agent never approves its own launcher. Only a reviewer verdict meeting
    ARIS's gate (score>=6 AND verdict in {ready,almost}) permits a freeze.
    """
    lp=wt/'programme'/'tasks'/tid/'TASK_LAUNCHER.md'
    outdir=SYN/'programme'/'waves'/'autonomous-wave-01'/'review'; outdir.mkdir(parents=True,exist_ok=True)
    jf=outdir/f'{tid}.round{rnd}.json'; log=outdir/f'{tid}.round{rnd}.log'
    cmd=[sys.executable,str(P/'launcher_review.py'),str(lp),'--task-id',tid,'--repo',str(SYN),
         '--round',str(rnd),'--json-out',str(jf)]
    fh=log.open('w')
    return subprocess.Popen(cmd,cwd=SYN,stdout=fh,stderr=subprocess.STDOUT,text=True,start_new_session=True),jf

def repair_start(tid,wt,verdict,rnd):
    """Hand the reviewer's REQUIRED changes back to a drafting agent. It may edit the
    launcher and implementation; it may not declare them acceptable."""
    import launcher_review as _lr
    prompt=(f"Task {tid} in {wt}. An INDEPENDENT adversarial reviewer scored its TASK_LAUNCHER.md "
            f"{verdict.get('score')}/10 with verdict '{verdict.get('verdict')}' and required these changes:\n\n"
            f"{_lr.findings_brief(verdict)}\n\n"
            "Apply every REQUIRED change to programme/tasks/{tid}/TASK_LAUNCHER.md and, where a finding "
            "concerns what the code does, to the implementation too. Do NOT run primary science, do not "
            "create primary output, and do not commit. Do not weaken or delete a control to satisfy a "
            "finding. Preserve the declared population, denominator and interpretation ceiling unless the "
            "reviewer explicitly required a change to them. If a finding would require genuinely new "
            "scientific scope that the tracked design packet does not cover, write "
            f"programme/tasks/{tid}/PREPARE_RESULT.json with status REVIEW_REQUIRED and stop. Otherwise "
            "keep PREPARE_RESULT.json status READY_TO_FREEZE and re-run its self-checks.").replace('{tid}',tid)
    cmd=shlex.split(os.environ.get('RETRON_PREPARE_COMMAND','claude --dangerously-skip-permissions -p'))+[prompt]
    log=SYN/'programme'/'waves'/'autonomous-wave-01'/'review'/f'{tid}.repair{rnd}.log'
    log.parent.mkdir(parents=True,exist_ok=True); fh=log.open('w')
    return subprocess.Popen(cmd,cwd=wt,stdout=fh,stderr=subprocess.STDOUT,text=True,start_new_session=True)

def contract_ok(tid,wt):
    """Machine-check the implementation can emit its required artefacts, BEFORE freeze."""
    import artefact_contract as _ac
    td=wt/'programme'/'tasks'/tid
    return _ac.check(td,td/'TASK_LAUNCHER.md')

def prepare_finish(tid,wt,base,plog,rc):
    """Validate a finished preparation. Raises ReviewRequired / RuntimeError as before."""
    out,err=plog
    if rc: raise RuntimeError(f'prepare rc={rc}; see {out} {err}')
    rp=wt/'programme'/'tasks'/tid/'PREPARE_RESULT.json'; d=json.loads(rp.read_text())
    if d.get('status')=='REVIEW_REQUIRED': raise ReviewRequired(d.get('unresolved_decision','unspecified'))
    if d.get('status')!='READY_TO_FREEZE': raise RuntimeError(f"PREPARE_RESULT status={d.get('status')!r}, expected READY_TO_FREEZE")
    d=normalise_prepare_result(d)
    if not self_checks_all_pass(d['self_checks']):
        bad=[c for c in d['self_checks'] if c.get('state')!='PASS']
        raise RuntimeError(f"PREPARE_RESULT self-checks not all PASS: {bad[:5]}")
    fm=parse_front_matter(wt/'programme'/'tasks'/tid/'TASK_LAUNCHER.md')
    if fm.get('base_commit')!=base or fm.get('frozen','').lower()!='true' or fm.get('state')!='AUTHORIZED': raise RuntimeError('prepared launcher not correctly bound/frozen')
    od=wt/fm['output_directory']
    if od.exists() and any(od.iterdir()): raise RuntimeError('prepare wrote primary output')
    return d
class ReviewRequired(RuntimeError):pass

def freeze(tid,wt,d):
    if not git('status','--porcelain',cwd=wt): raise RuntimeError('prepare made no changes')
    run(['git','add',f'programme/tasks/{tid}'],cwd=wt); run(['git','commit','-m',f'freeze: {tid}'],cwd=wt); sha=git('rev-parse','HEAD',cwd=wt)
    tracked=git('ls-tree','-r','--name-only','HEAD','--',f'programme/tasks/{tid}',cwd=wt).splitlines(); frozen={r:sha256_file(wt/r) for r in tracked if (wt/r).is_file()}
    fm=parse_front_matter(wt/'programme'/'tasks'/tid/'TASK_LAUNCHER.md'); spec={'schema_version':1,'task_id':tid,'worktree':str(wt),'branch':f'task/{tid}','freeze_commit':sha,'command':d['command'],'inputs':d['inputs'],'output_directory':fm['output_directory'],'backend':d['backend'],'resources':d['resources'],'runtime':d['runtime'],'frozen_files':frozen}
    sp=EXEC/tid/'TASK_EXECUTION.json'; sp.parent.mkdir(parents=True,exist_ok=True); atomic_write(sp,json.dumps(spec,indent=2,sort_keys=True)+'\n'); return sha,sp

def spawn(tid,sp,w):
    rd=w.parent/'runs'; rd.mkdir(exist_ok=True); rec=rd/f'{tid}.json'; log=rd/f'{tid}.worker.log'; env=os.environ.copy(); env['RETRON_RUNTIME_RECORD']=str(rec)
    # Clear any record from a PREVIOUS attempt. If this launch refuses before the worker
    # writes (e.g. launch_task.sh bails), a leftover record would be read as THIS attempt's
    # outcome -- which is how a re-run of T-R2a was voided by a 20-minute-old result.
    rec.unlink(missing_ok=True)
    with log.open('ab') as fh:
        proc=subprocess.Popen(['bash',str(P/'launch_task.sh'),tid,'--execute','--execution-spec',str(sp)],cwd=SYN,env=env,stdout=fh,stderr=subprocess.STDOUT,start_new_session=True)
    return proc,rec

def dry(w):
    wr=rows(w); b=board(); states={k:v['state'] for k,v in b.items()}; used=0; tasks=[]; print('wave_sha256\t'+sha256_file(w)); print('nvme_tokens\t'+str(tokens()))
    for r in wr:
        if r['action']=='monitor_only':
            ok=alive(int(r.get('monitor_pid') or 0)); used+=int(r['io_tokens']) if ok else 0; states[r['task_id']]='RUNNING' if ok else states.get(r['task_id'],'UNKNOWN'); print(f"{r['task_id']}\tMONITOR_ONLY\talive={ok}\tio={r['io_tokens']}")
        else:tasks.append(ScheduleTask(r['task_id'],b.get(r['task_id'],{}).get('state','MISSING'),int(r['io_tokens']),split(r['hard_dependencies']),split(r['schedule_after'])))
    # Preview the REAL admission path: dependencies unbounded, then broker routing across
    # both pools, exactly as start() does. Anything else is a misleading rehearsal.
    broker=make_broker(); by={r['task_id']:r for r in wr}
    snap=broker.snapshot(used)
    print('local_pool\t'+json.dumps(snap['local'],sort_keys=True))
    print('ibex_pool\t'+json.dumps(snap['ibex'],sort_keys=True))
    eligible,dec=choose_launchable(tasks,states,0,1<<30)
    sel=[]; drain=False
    for tid in eligible:
        pl=broker.plan(tid,io_tokens=int(by[tid]['io_tokens']),
                       declared_backend=by[tid].get('backend','auto'),nvme_used=used)
        if pl.backend=='defer':
            drain=drain or pl.drain; dec[tid]=f'WAIT_RESOURCE:{pl.reason}'; continue
        if drain and pl.backend=='local':
            dec[tid]='WAIT_RESOURCE:draining local pool for an exclusive window'; continue
        dec[tid]=f'SELECTED->{pl.backend} ({pl.reason})'; sel.append(tid)
        if pl.backend=='local': used+=pl.nvme_cost
    for t in sorted(tasks,key=lambda x:x.task_id): print(f"{t.task_id}\t{dec.get(t.task_id,'NOT_ELIGIBLE')}\tboard={b.get(t.task_id,{}).get('state','MISSING')}\tio={t.io_tokens}")
    print('selected\t'+';'.join(sel)); return 0

def start(w,authorised,poll):
    if git('rev-parse','--abbrev-ref','HEAD')!='project-synthesis' or git('status','--porcelain'): raise RuntimeError('start requires clean project-synthesis')
    if sha256_file(w)!=authorised: raise RuntimeError('WAVE.tsv hash mismatch')
    wr=rows(w); st=load_status(w); [st.setdefault(r['task_id'],{**{k:'' for k in STATUS_FIELDS},'task_id':r['task_id'],'state':'PENDING'}) for r in wr]; save_status(w,st); commit([status_path(w)],'wave: start '+w.parent.name); aris_start(w,[r['task_id'] for r in wr])
    workers={}; preparing={}; reviewing={}; repairing={}; plans={}; retries={}; escal=False
    broker=make_broker()
    # RESTART RECONCILIATION, from disk alone. A coordinator that died mid-flight leaves
    # board=RUNNING and status=RUNNING/PREPARING/REVIEWING/REPAIRING behind. No worker of
    # ours survives a restart, so any such row is stale by definition: requeue it rather
    # than leaving the task permanently unschedulable.
    _b0=board()
    for r in wr:
        tid=r['task_id']
        if r['action']=='monitor_only': continue
        if _b0.get(tid,{}).get('state')=='RUNNING':
            set_board(tid,'AUTHORIZED','requeued: coordinator restarted while it was RUNNING')
        if st.get(tid,{}).get('state') in {'RUNNING','PREPARING','REVIEWING','REPAIRING'}:
            set_status(w,st,tid,'PENDING','requeued after coordinator restart',worker_pid='',analysis_pid='')
    commit([BOARD,status_path(w)],'wave: reconcile stale in-flight state on restart')
    while True:
        b=board(); states={k:v['state'] for k,v in b.items()}; used=0
        for r in wr:
            if r['action']=='monitor_only':
                pid=int(r.get('monitor_pid') or 0)
                if alive(pid): used+=int(r['io_tokens']); states[r['task_id']]='RUNNING'; set_status(w,st,r['task_id'],'RUNNING_EXTERNAL',f'monitor-only pid={pid}; no signals')
                elif st[r['task_id']]['state']!='ESCALATION_REQUIRED': set_status(w,st,r['task_id'],'ESCALATION_REQUIRED','external process exited; finalise under durable handoff'); escal=True
        # Collect finished preparation agents. They run concurrently with each other and
        # with executing workers; only the short freeze step is serialised here.
        for tid,(pproc,wt,base,plog,cost) in list(preparing.items()):
            if pproc.poll() is None: used+=cost; continue
            del preparing[tid]
            try:
                d=prepare_finish(tid,wt,base,plog,pproc.returncode)
                ok,cchecks=contract_ok(tid,wt)
                if not ok:
                    bad=[c['check'] for c in cchecks if c['result']=='FAIL']
                    raise RuntimeError(f'artefact contract would fail at runtime: {bad}')
                # Author != approver: nothing freezes until an independent reviewer says so.
                rp,jf=review_start(tid,wt,1); reviewing[tid]=(rp,wt,d,1,jf,cost)
                set_status(w,st,tid,'REVIEWING','independent adversarial review round 1')
            except ReviewRequired as e:set_board(tid,'BLOCKED',f'scientific review required: {e}'); set_status(w,st,tid,'BLOCKED',str(e)); commit([BOARD,status_path(w)],f'wave: scientific stop {tid}'); escal=True
            except Exception as e:set_status(w,st,tid,'BLOCKED_PREPARE',str(e)); escal=True
        # Collect finished adversarial reviews.
        for tid,(rproc,wt,d,rnd,jf,cost) in list(reviewing.items()):
            if rproc.poll() is None: used+=cost; continue
            del reviewing[tid]
            import launcher_review as _lr
            try: v=json.loads(jf.read_text())
            except Exception as e: v={'score':0,'verdict':'not ready','findings':[],'reviewer_ran':False,'error':str(e)}
            if _lr.accepted(v):
                try:
                    fr,sp=freeze(tid,wt,d)
                    fm=parse_front_matter(wt/'programme'/'tasks'/tid/'TASK_LAUNCHER.md')
                    ledger(tid,question_short=fm.get('title',tid),freeze_commit=fr,state='FROZEN_NOT_EXECUTED',backend=d['backend'],primary_output=fm.get('output_directory',''),interpretation_ceiling='SEE_TASK_LAUNCHER')
                    set_status(w,st,tid,'FROZEN',f"review {v['score']}/10 {v['verdict']} round {rnd}",freeze_commit=fr)
                    commit([sp,LEDGER,status_path(w)],f'wave: bind {tid} after independent review')
                except Exception as e:set_status(w,st,tid,'BLOCKED_PREPARE',str(e)); escal=True
            elif rnd>=_lr.MAX_ROUNDS:
                # ⛔ Never freeze past the gate. Park this task; everything else continues.
                set_board(tid,'PARKED_REVIEW_GATE',f"adversarial review did not reach score>=6 AND ready|almost in {rnd} rounds")
                set_status(w,st,tid,'PARKED_REVIEW_GATE',f"last: {v.get('score')}/10 {v.get('verdict')} — {v.get('summary','')[:120]}")
                commit([BOARD,status_path(w)],f'wave: park {tid} at the review gate'); escal=True
            else:
                repairing[tid]=(repair_start(tid,wt,v,rnd),wt,d,rnd+1,cost)
                set_status(w,st,tid,'REPAIRING',f"round {rnd}: {v.get('score')}/10 {v.get('verdict')}; repairing findings")
        # Collect finished repairs and send them back for re-review.
        for tid,(qproc,wt,d,rnd,cost) in list(repairing.items()):
            if qproc.poll() is None: used+=cost; continue
            del repairing[tid]
            rpath=wt/'programme'/'tasks'/tid/'PREPARE_RESULT.json'
            try:
                nd=json.loads(rpath.read_text())
                if nd.get('status')=='REVIEW_REQUIRED':
                    set_board(tid,'BLOCKED',f"new scientific scope: {nd.get('unresolved_decision','')}")
                    set_status(w,st,tid,'BLOCKED',str(nd.get('unresolved_decision',''))[:200]); escal=True; continue
                d=normalise_prepare_result(nd)
            except Exception: pass
            rp,jf=review_start(tid,wt,rnd); reviewing[tid]=(rp,wt,d,rnd,jf,cost)
            set_status(w,st,tid,'REVIEWING',f'independent adversarial review round {rnd}')
        for tid,(proc,rec,cost) in list(workers.items()):
            if proc.poll() is None: used+=cost; continue
            rr=json.loads(rec.read_text()) if rec.exists() else {'worker_state':'REFUSED','error':'missing run record'}; spec=load_execution_spec(EXEC/tid/'TASK_EXECUTION.json')
            if rr.get('worker_state')=='COMPLETE':
                self_reported=rr['task_state']; term=executor_terminal_state(self_reported)
                aris_set(w,tid,'done',rr.get('task_report',''))
                note='autonomous wave; executor self-report, NOT an acceptance' if term!=self_reported else 'autonomous wave'
                if term=='COMPLETE_AWAITING_REVIEW':
                    term,note=deterministic_accept(tid,spec,w,st) or (term,note)
                set_board(tid,term,note); set_status(w,st,tid,term,rr.get('scientific_outcome',''),finished_at=rr.get('finished_at',utc()))
            else:
                # A launch that never produced a run record may have been refused by a
                # transient mechanical gate rather than by anything scientific. Retry those;
                # never retry a failed control or a real criterion failure.
                sig=transient_reason(tid,w) if not rec.exists() else ''
                n=retries.get(tid,0)
                if sig and n<MAX_TRANSIENT_RETRIES:
                    retries[tid]=n+1
                    # The board is the scheduling authority; leaving it at RUNNING after a
                    # refused launch made the task permanently unschedulable across restarts.
                    set_board(tid,'AUTHORIZED',f'transient launch failure ({sig}); requeued')
                    set_status(w,st,tid,'FROZEN',f'transient launch failure ({sig}); retry {n+1}/{MAX_TRANSIENT_RETRIES}')
                    del workers[tid]; continue
                # A governance gate can fail because the task worktree predates a repo-level
                # fix: worktree() only rebases during PREPARE, so an already-frozen task can
                # never pick one up. Re-freezing on the current base is a mechanical repair
                # that touches no scientific design, so do it once instead of dying here.
                if sig and stale_base(tid):
                    sp_stale=EXEC/tid/'TASK_EXECUTION.json'; sp_stale.unlink(missing_ok=True)
                    retries[tid]=0
                    set_board(tid,'AUTHORIZED','worktree predates a governance fix; re-freezing on the current base')
                    set_status(w,st,tid,'PENDING',f'"{sig}" and the worktree base is stale; re-preparing on current HEAD')
                    commit([BOARD,status_path(w)],f'wave: re-freeze {tid} on a corrected base')
                    del workers[tid]; continue
                term='VOID' if rr.get('worker_state') in {'REFUSED','ARTIFACT_INVALID','PROCESS_FAILED'} else 'STOP'
                detail=rr.get('error') or rr.get('stop_reason') or rr.get('worker_state','')
                if sig: detail=f'{detail}; transient signature "{sig}" persisted after {n} retries'
                set_board(tid,term,rr.get('worker_state','worker failure')); set_status(w,st,tid,term,detail); aris_set(w,tid,'failed'); escal=True
            ledger(tid,freeze_commit=spec['freeze_commit'],execution_commit=spec['freeze_commit'],state=term,backend=spec['backend'],primary_output=spec['output_directory'],task_report=str(Path(spec['output_directory'])/'TASK_REPORT.md'),interpretation_ceiling='SEE_TASK_REPORT',started_at=rr.get('started_at',''),finished_at=rr.get('finished_at',utc())); commit([BOARD,LEDGER,status_path(w)],f'wave: terminal {tid} {term}'); del workers[tid]
        b=board(); states={k:v['state'] for k,v in b.items()}; candidates=[]; by={r['task_id']:r for r in wr}
        for r in wr:
            tid=r['task_id']; cur=st[tid]['state']
            # A preparing task already reserves its tokens in the collection loop above, so
            # it must not also compete for them here; it re-enters as a candidate once FROZEN.
            if r['action']=='monitor_only' or tid in workers or tid in preparing or tid in reviewing or tid in repairing or cur in TERMINAL|{'RUNNING_EXTERNAL','ESCALATION_REQUIRED','BLOCKED_PREPARE','PARKED_REVIEW_GATE','PARKED_LAUNCHER_REVIEW'}: continue
            candidates.append(ScheduleTask(tid,b.get(tid,{}).get('state',cur),int(r['io_tokens']),split(r['hard_dependencies']),split(r['schedule_after'])))
        # DEPENDENCIES first, with resources deliberately unbounded: choose_launchable decides
        # only what is scientifically eligible. ADMISSION is then the broker's, across BOTH
        # pools, so an Ibex-bound task is not gated by local I/O and vice versa.
        eligible,dec=choose_launchable(candidates,states,0,1<<30)
        sel=[]; drain=False
        for tid in eligible:
            r=by[tid]; fm={}
            spf=EXEC/tid/'TASK_EXECUTION.json'
            if spf.exists():
                try: fm=load_execution_spec(spf)
                except Exception: fm={}
            res=(fm.get('resources') or {}); want=(fm.get('backend') or by[tid].get('backend') or 'auto')
            pl=broker.plan(tid,io_tokens=int(r['io_tokens']),declared_backend=want,
                           cpu_threads=int(res.get('cpu_threads',1) or 1),
                           memory_gb=int(res.get('memory_gb',4) or 4),
                           gpu=bool(res.get('gpu_slots',0)),
                           nvme_used=used,local_running=len(workers))
            plans[tid]=pl
            if pl.backend=='defer':
                drain=drain or pl.drain
                dec[tid]=f'WAIT_RESOURCE:{pl.reason}'
                continue
            if drain and pl.backend=='local':
                # A drain window is open for a task that needs the whole local pool; stop
                # admitting new LOCAL work so it can actually start. Ibex work still flows.
                dec[tid]=f'WAIT_RESOURCE:draining local pool for an exclusive window'
                continue
            sel.append(tid)
            if pl.backend=='local': used+=pl.nvme_cost
        for t in candidates:
            if t.task_id not in sel:set_status(w,st,t.task_id,'BLOCKED' if dec.get(t.task_id,'').startswith('BLOCKED_DEPENDENCY') else ('WAIT_RESOURCE' if dec.get(t.task_id,'').startswith('WAIT_RESOURCE') else 'WAIT_DEP'),dec.get(t.task_id,''))
        for tid in sel:
            r=by[tid]; sp=EXEC/tid/'TASK_EXECUTION.json'
            if not sp.exists():
                # Preparation is started ASYNCHRONOUSLY and collected in the poll loop above.
                # Running it inline blocked every other task behind one prepare agent, which
                # left finished workers unreaped and eligible frozen science idle for minutes.
                if tid not in preparing:
                    # Authoring stages cost ONE token, not the task's execution budget.
                    # Reserving all 8 while merely writing a launcher starved every other
                    # task -- and did so even for a task routed to Ibex, which will consume
                    # no local I/O at all. Execution reserves the real cost.
                    try: wt=worktree(tid); proc,plog=prepare_start(tid,{**r,'_wave':w},wt); preparing[tid]=(proc,wt,git('rev-parse','HEAD'),plog,AUTHORING_COST); set_status(w,st,tid,'PREPARING',f'prepare agent pid={proc.pid}')
                    except Exception as e:set_status(w,st,tid,'BLOCKED_PREPARE',str(e)); escal=True
                continue
            spec=load_execution_spec(sp); fm=parse_front_matter(Path(spec['worktree'])/'programme'/'tasks'/tid/'TASK_LAUNCHER.md'); protected=fm.get('confirmatory_spend','').lower().startswith('yes') or 'required' in fm.get('confirmatory_spend','').lower()
            if protected and r.get('protected_spend_authorised','').lower()!='true':set_status(w,st,tid,'BLOCKED','protected spend not authorised'); escal=True; continue
            # The broker's routing decision is authoritative and is written into the frozen
            # spec before launch, so the ledger records the backend the task ACTUALLY ran on.
            pl=plans.get(tid)
            if pl and pl.backend in ('local','ibex') and spec.get('backend')!=pl.backend:
                spec['backend']=pl.backend; atomic_write(sp,json.dumps(spec,indent=2,sort_keys=True)+'\n')
            set_board(tid,'RUNNING','autonomous wave'); p,rec=spawn(tid,sp,w); workers[tid]=(p,rec,int(r['io_tokens'])); ledger(tid,freeze_commit=spec['freeze_commit'],execution_commit=spec['freeze_commit'],state='RUNNING',backend=spec['backend'],primary_output=spec['output_directory'],task_report=str(Path(spec['output_directory'])/'TASK_REPORT.md'),interpretation_ceiling='SEE_TASK_LAUNCHER',started_at=utc()); set_status(w,st,tid,'RUNNING',f"worker launched on {spec['backend']} ({pl.reason if pl else 'declared'})",freeze_commit=spec['freeze_commit'],worker_pid=p.pid,started_at=utc()); aris_set(w,tid,'running'); commit([BOARD,LEDGER,status_path(w)],f'wave: launch {tid} on {spec["backend"]}')
        if not workers and not preparing and not reviewing and not repairing:
            non=[st[r['task_id']]['state'] for r in wr if r['action']!='monitor_only']
            if not any(x in {'PENDING','AUTHORIZED','FROZEN','PREPARING','REVIEWING','REPAIRING'} for x in non): commit([status_path(w)],'wave: checkpoint '+w.parent.name); return 4 if escal or any(x.startswith('WAIT_') or x.startswith('BLOCKED') for x in non) else 0
        time.sleep(poll)

def main():
    a=argparse.ArgumentParser(); a.add_argument('wave',type=Path); g=a.add_mutually_exclusive_group(required=True); g.add_argument('--dry-run',action='store_true'); g.add_argument('--start',action='store_true'); g.add_argument('--status',action='store_true'); a.add_argument('--authorise-wave-sha256'); a.add_argument('--poll-seconds',type=int,default=5); x=a.parse_args(); w=x.wave.resolve()
    if x.dry_run:return dry(w)
    if x.status:
        for tid,r in sorted(load_status(w).items()):print(tid,r.get('state',''),r.get('detail',''),sep='\t')
        return 0
    if not x.authorise_wave_sha256:raise SystemExit('--start requires --authorise-wave-sha256')
    f=lock()
    try:return start(w,x.authorise_wave_sha256,x.poll_seconds)
    finally:fcntl.flock(f.fileno(),fcntl.LOCK_UN); f.close()
if __name__=='__main__': raise SystemExit(main())
