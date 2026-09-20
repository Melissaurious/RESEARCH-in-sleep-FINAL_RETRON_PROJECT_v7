#!/usr/bin/env python3
"""Thin autonomous wave coordinator. No scientific decisions live here."""
from __future__ import annotations
import argparse, csv, fcntl, hashlib, json, os, shlex, subprocess, sys, time
from datetime import datetime, timezone
from pathlib import Path
from autonomy_state import TERMINAL, ScheduleTask, acceptance_verdict, atomic_write, choose_launchable, executor_terminal_state, load_execution_spec, parse_front_matter, read_tsv, sha256_file, upsert_tsv, validate_type_a_execution, write_tsv

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
def tokens():
    for r in rows(LIMITS):
        if r['resource']=='NVME_TOKENS': return int(r['capacity'])
    raise RuntimeError('NVME_TOKENS missing')
def lock():
    p=Path(git('rev-parse','--git-common-dir')).resolve()/'retron-autonomous-wave.lock'; f=p.open('w'); fcntl.flock(f.fileno(),fcntl.LOCK_EX|fcntl.LOCK_NB); f.write(f'pid={os.getpid()} {utc()}\n'); f.flush(); return f

def worktree(tid):
    fm=parse_front_matter(P/'tasks'/tid/'TASK_LAUNCHER.md'); wt=Path(fm.get('worktree','')) if fm.get('worktree') else SYN.parent/f"{SYN.name.removesuffix('-synthesis')}-{tid}"; br=f'task/{tid}'; base=git('rev-parse','HEAD')
    if wt.exists():
        if git('rev-parse','--abbrev-ref','HEAD',cwd=wt)!=br or git('status','--porcelain',cwd=wt): raise RuntimeError(f'unsafe existing worktree {wt}')
    else:
        exists=run(['git','show-ref','--verify','--quiet',f'refs/heads/{br}'],check=False).returncode==0
        run(['git','worktree','add',str(wt),br] if exists else ['git','worktree','add','-b',br,str(wt),base])
    if run(['git','merge-base','--is-ancestor',base,'HEAD'],cwd=wt,check=False).returncode:
        p=run(['git','rebase',base],cwd=wt,check=False)
        if p.returncode: run(['git','rebase','--abort'],cwd=wt,check=False); raise RuntimeError(f'rebase failed: {p.stderr.strip()}')
    return wt

def prepare(tid,row,wt):
    base=git('rev-parse','HEAD'); refs='\n'.join('  - '+x for x in split(row['design_refs']))
    prompt=f'''Prepare exactly task {tid} in {wt}. DO NOT run primary science. Read its TASK_LAUNCHER.md, {P/'WORKING_RULES.md'}, {SYN/'review-stage/TASK_PROTOCOL.md'}, and:\n{refs}\nCurrent authoritative project-synthesis base is {base}. Preserve approved science. Ordinary implementation choices are autonomous. If a genuinely new biological endpoint/threshold/population decision is needed, write programme/tasks/{tid}/PREPARE_RESULT.json with status REVIEW_REQUIRED and stop. Otherwise implement code+fixtures, run only self-checks, update launcher to base_commit={base}, base_branch=project-synthesis, state=AUTHORIZED, frozen=true; do not create primary output and do not commit. The launcher front matter MUST declare autonomy_tier: A for a preregistered computation whose acceptance gate is fully machine-verifiable (frozen hashes, input hashes, blocking controls, manifest, run log, report schema), or autonomy_tier: B if accepting it needs a human/cross-model judgment of merit or interpretation; tier A is then accepted by deterministic validation alone, tier B waits for semantic review. Write PREPARE_RESULT.json schema_version=1, status=READY_TO_FREEZE, task_id, command argv, inputs(dataset_id,path,sha256), backend, resources(cpu_threads,memory_gb,io_tokens={row['io_tokens']}), runtime(max_runtime_seconds,resume_allowed,stop_note), self_checks, unresolved_decision.'''
    cmd=shlex.split(os.environ.get('RETRON_PREPARE_COMMAND','claude --dangerously-skip-permissions -p'))+[prompt]
    log=row['_wave'].parent/'prepare_logs'; log.mkdir(exist_ok=True); out=log/f'{tid}.stdout.log'; err=log/f'{tid}.stderr.log'
    with out.open('w') as o,err.open('w') as e:p=subprocess.run(cmd,cwd=wt,stdout=o,stderr=e,text=True)
    if p.returncode: raise RuntimeError(f'prepare rc={p.returncode}; see {out} {err}')
    rp=wt/'programme'/'tasks'/tid/'PREPARE_RESULT.json'; d=json.loads(rp.read_text())
    if d.get('status')=='REVIEW_REQUIRED': raise ReviewRequired(d.get('unresolved_decision','unspecified'))
    if d.get('status')!='READY_TO_FREEZE' or any(x.get('state')!='PASS' for x in d.get('self_checks',[])): raise RuntimeError('PREPARE_RESULT not ready')
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
    with log.open('ab') as fh:
        proc=subprocess.Popen(['bash',str(P/'launch_task.sh'),tid,'--execute','--execution-spec',str(sp)],cwd=SYN,env=env,stdout=fh,stderr=subprocess.STDOUT,start_new_session=True)
    return proc,rec

def dry(w):
    wr=rows(w); b=board(); states={k:v['state'] for k,v in b.items()}; used=0; tasks=[]; print('wave_sha256\t'+sha256_file(w)); print('nvme_tokens\t'+str(tokens()))
    for r in wr:
        if r['action']=='monitor_only':
            ok=alive(int(r.get('monitor_pid') or 0)); used+=int(r['io_tokens']) if ok else 0; states[r['task_id']]='RUNNING' if ok else states.get(r['task_id'],'UNKNOWN'); print(f"{r['task_id']}\tMONITOR_ONLY\talive={ok}\tio={r['io_tokens']}")
        else:tasks.append(ScheduleTask(r['task_id'],b.get(r['task_id'],{}).get('state','MISSING'),int(r['io_tokens']),split(r['hard_dependencies']),split(r['schedule_after'])))
    sel,dec=choose_launchable(tasks,states,used,tokens())
    for t in sorted(tasks,key=lambda x:x.task_id): print(f"{t.task_id}\t{dec.get(t.task_id,'NOT_ELIGIBLE')}\tboard={b.get(t.task_id,{}).get('state','MISSING')}\tio={t.io_tokens}")
    print('selected\t'+';'.join(sel)); return 0

def start(w,authorised,poll):
    if git('rev-parse','--abbrev-ref','HEAD')!='project-synthesis' or git('status','--porcelain'): raise RuntimeError('start requires clean project-synthesis')
    if sha256_file(w)!=authorised: raise RuntimeError('WAVE.tsv hash mismatch')
    wr=rows(w); st=load_status(w); [st.setdefault(r['task_id'],{**{k:'' for k in STATUS_FIELDS},'task_id':r['task_id'],'state':'PENDING'}) for r in wr]; save_status(w,st); commit([status_path(w)],'wave: start '+w.parent.name); aris_start(w,[r['task_id'] for r in wr])
    workers={}; escal=False
    while True:
        b=board(); states={k:v['state'] for k,v in b.items()}; used=0
        for r in wr:
            if r['action']=='monitor_only':
                pid=int(r.get('monitor_pid') or 0)
                if alive(pid): used+=int(r['io_tokens']); states[r['task_id']]='RUNNING'; set_status(w,st,r['task_id'],'RUNNING_EXTERNAL',f'monitor-only pid={pid}; no signals')
                elif st[r['task_id']]['state']!='ESCALATION_REQUIRED': set_status(w,st,r['task_id'],'ESCALATION_REQUIRED','external process exited; finalise under durable handoff'); escal=True
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
            else: term='VOID' if rr.get('worker_state') in {'REFUSED','ARTIFACT_INVALID','PROCESS_FAILED'} else 'STOP'; set_board(tid,term,rr.get('worker_state','worker failure')); set_status(w,st,tid,term,rr.get('error') or rr.get('stop_reason') or rr.get('worker_state','')); aris_set(w,tid,'failed'); escal=True
            ledger(tid,freeze_commit=spec['freeze_commit'],execution_commit=spec['freeze_commit'],state=term,backend=spec['backend'],primary_output=spec['output_directory'],task_report=str(Path(spec['output_directory'])/'TASK_REPORT.md'),interpretation_ceiling='SEE_TASK_REPORT',started_at=rr.get('started_at',''),finished_at=rr.get('finished_at',utc())); commit([BOARD,LEDGER,status_path(w)],f'wave: terminal {tid} {term}'); del workers[tid]
        b=board(); states={k:v['state'] for k,v in b.items()}; candidates=[]; by={r['task_id']:r for r in wr}
        for r in wr:
            tid=r['task_id']; cur=st[tid]['state']
            if r['action']=='monitor_only' or tid in workers or cur in TERMINAL|{'RUNNING_EXTERNAL','ESCALATION_REQUIRED','BLOCKED_PREPARE'}: continue
            candidates.append(ScheduleTask(tid,b.get(tid,{}).get('state',cur),int(r['io_tokens']),split(r['hard_dependencies']),split(r['schedule_after'])))
        sel,dec=choose_launchable(candidates,states,used,tokens())
        for t in candidates:
            if t.task_id not in sel:set_status(w,st,t.task_id,'BLOCKED' if dec.get(t.task_id,'').startswith('BLOCKED_DEPENDENCY') else ('WAIT_RESOURCE' if dec.get(t.task_id,'').startswith('WAIT_RESOURCE') else 'WAIT_DEP'),dec.get(t.task_id,''))
        for tid in sel:
            r=by[tid]; sp=EXEC/tid/'TASK_EXECUTION.json'
            if not sp.exists():
                try: wt=worktree(tid); d=prepare(tid,{**r,'_wave':w},wt); fr,sp=freeze(tid,wt,d); ledger(tid,question_short=parse_front_matter(wt/'programme'/'tasks'/tid/'TASK_LAUNCHER.md').get('title',tid),freeze_commit=fr,state='FROZEN_NOT_EXECUTED',backend=d['backend'],primary_output=parse_front_matter(wt/'programme'/'tasks'/tid/'TASK_LAUNCHER.md').get('output_directory',''),interpretation_ceiling='SEE_TASK_LAUNCHER'); set_status(w,st,tid,'FROZEN','ready',freeze_commit=fr); commit([sp,LEDGER,status_path(w)],f'wave: bind {tid}')
                except ReviewRequired as e:set_board(tid,'BLOCKED',f'scientific review required: {e}'); set_status(w,st,tid,'BLOCKED',str(e)); commit([BOARD,status_path(w)],f'wave: scientific stop {tid}'); escal=True; continue
                except Exception as e:set_status(w,st,tid,'BLOCKED_PREPARE',str(e)); escal=True; continue
            spec=load_execution_spec(sp); fm=parse_front_matter(Path(spec['worktree'])/'programme'/'tasks'/tid/'TASK_LAUNCHER.md'); protected=fm.get('confirmatory_spend','').lower().startswith('yes') or 'required' in fm.get('confirmatory_spend','').lower()
            if protected and r.get('protected_spend_authorised','').lower()!='true':set_status(w,st,tid,'BLOCKED','protected spend not authorised'); escal=True; continue
            set_board(tid,'RUNNING','autonomous wave'); p,rec=spawn(tid,sp,w); workers[tid]=(p,rec,int(r['io_tokens'])); ledger(tid,freeze_commit=spec['freeze_commit'],execution_commit=spec['freeze_commit'],state='RUNNING',backend=spec['backend'],primary_output=spec['output_directory'],task_report=str(Path(spec['output_directory'])/'TASK_REPORT.md'),interpretation_ceiling='SEE_TASK_LAUNCHER',started_at=utc()); set_status(w,st,tid,'RUNNING','worker launched',freeze_commit=spec['freeze_commit'],worker_pid=p.pid,started_at=utc()); aris_set(w,tid,'running'); commit([BOARD,LEDGER,status_path(w)],f'wave: launch {tid}')
        if not workers:
            non=[st[r['task_id']]['state'] for r in wr if r['action']!='monitor_only']
            if not any(x in {'PENDING','AUTHORIZED','FROZEN','PREPARING'} for x in non): commit([status_path(w)],'wave: checkpoint '+w.parent.name); return 4 if escal or any(x.startswith('WAIT_') or x.startswith('BLOCKED') for x in non) else 0
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
