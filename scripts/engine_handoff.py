#!/usr/bin/env python3
"""Maintain a resumable engine integration journal for one art run."""
from __future__ import annotations
import argparse, json
from datetime import datetime, timezone
from pathlib import Path


def now():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00','Z')


def load(path: Path):
    return json.loads(path.read_text(encoding='utf-8'))


def save(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + '.tmp')
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    tmp.replace(path)


def run_path(args):
    return Path(args.run_dir).resolve()


def handoff_path(run: Path):
    return run / 'engine-handoff.json'


def rel(run: Path, value: str):
    p = Path(value)
    p = p if p.is_absolute() else run / p
    try:
        return p.resolve().relative_to(run).as_posix()
    except ValueError:
        return str(p.resolve())


def sync_manifest(run: Path, h):
    path = run / 'manifest.json'
    if not path.exists():
        return
    m = load(path)
    e = m.setdefault('engine', {})
    e['adapter'] = h.get('adapter')
    e['imports'] = [{k:i.get(k) for k in ('source','target','status','asset_uuid','spriteframe_uuid')} for i in h.get('imports', [])]
    if e['imports'] and all(i['status'] == 'imported' for i in e['imports']):
        e['readback'] = {'status':'pass','import_count':len(e['imports']),'updated_at':now()}
    else:
        e['readback'] = None
    if h.get('preview',{}).get('status') != 'pending':
        e['preview'] = h.get('preview')
    save(path, m)


def final_assets(run: Path):
    p = run / 'manifest.json'
    if not p.exists():
        return []
    out = []
    for item in load(p).get('final_assets', []):
        value = item.get('path') if isinstance(item, dict) else item
        if value:
            out.append(str(value))
    return out


def get_handoff(run: Path):
    p = handoff_path(run)
    if not p.exists():
        raise SystemExit(f'missing {p}; run init first')
    return p, load(p)


def cmd_init(a):
    run = run_path(a); p = handoff_path(run)
    if p.exists() and not a.force:
        print(p); return 0
    sources = (final_assets(run) if a.from_final_assets else []) + a.asset
    seen, imports = set(), []
    for source in sources:
        s = rel(run, source)
        if s in seen: continue
        seen.add(s)
        name = Path(source).name
        target = f"{a.target_root.rstrip('/\\')}/{name}".replace('\\','/') if a.target_root else None
        imports.append({'source':s,'target':target,'status':'pending','asset_uuid':None,'spriteframe_uuid':None,'attempts':[],'readback':None})
    h = {
        'schema_version':1,'engine_type':a.engine_type,'adapter':a.adapter,'adapter_tier':a.adapter_tier,
        'status':'prepared','created_at':now(),'updated_at':now(),
        'policy':{'import_batch_size':a.import_batch_size,'import_timeout_seconds':a.import_timeout_seconds,
                  'import_max_retries':a.import_max_retries,'animation_strategy':a.animation_strategy,
                  'allow_runtime_sequence_fallback':a.allow_runtime_sequence_fallback},
        'imports':imports,'animations':[],
        'runtime_object':{'status':'pending','path':None,'uuid':None,'readback':None},
        'preview':{'status':'pending','path':None,'instances':0,'console_errors':None,'console_warnings':None,'note':None},
        'notes':[]}
    save(p,h); sync_manifest(run,h); print(p); return 0


def cmd_set_adapter(a):
    run=run_path(a); p,h=get_handoff(run)
    if a.adapter: h['adapter']=a.adapter
    if a.tier: h['adapter_tier']=a.tier
    h['updated_at']=now(); save(p,h); sync_manifest(run,h); print(p); return 0


def cmd_next_batch(a):
    run=run_path(a); _,h=get_handoff(run); policy=h.get('policy',{})
    size=a.size or int(policy.get('import_batch_size',4)); maxr=int(policy.get('import_max_retries',2))
    items=[]; exhausted=[]
    for i in h.get('imports',[]):
        if i.get('status') in {'imported','importing'}: continue
        fails=sum(1 for x in i.get('attempts',[]) if x.get('status') in {'failed','timeout'})
        if fails > maxr: exhausted.append(i.get('source')); continue
        items.append({'source':i.get('source'),'target':i.get('target'),'status':i.get('status'),'attempts':len(i.get('attempts',[]))})
    print(json.dumps({'batch_size':size,'items':items[:size],'remaining_after_batch':max(0,len(items)-size),'exhausted':exhausted},ensure_ascii=False,indent=2))
    return 0


def find_import(h, run, source):
    s=rel(run,source)
    for i in h.get('imports',[]):
        if i.get('source')==s: return i
    raise SystemExit(f'source not in import plan: {s}')


def cmd_record_import(a):
    run=run_path(a); p,h=get_handoff(run); i=find_import(h,run,a.source)
    if a.target: i['target']=a.target.replace('\\','/')
    i['status']=a.status
    if a.asset_uuid: i['asset_uuid']=a.asset_uuid
    if a.spriteframe_uuid: i['spriteframe_uuid']=a.spriteframe_uuid
    i.setdefault('attempts',[]).append({'at':now(),'status':a.status,'message':a.message})
    if a.readback_json: i['readback']=load(Path(a.readback_json).resolve())
    elif a.status=='imported': i['readback']={'status':'pass','asset_uuid':i.get('asset_uuid'),'spriteframe_uuid':i.get('spriteframe_uuid')}
    if h.get('imports') and all(x.get('status')=='imported' for x in h['imports']): h['status']='assets-imported'
    h['updated_at']=now(); save(p,h); sync_manifest(run,h); print(p); return 0


def upsert_anim(h, aid):
    for i in h.get('animations',[]):
        if i.get('id')==aid: return i
    i={'id':aid,'status':'pending','strategy':None,'asset_uuid':None,'runtime_object':None,'frame_count':None,'readback':None,'message':None}
    h.setdefault('animations',[]).append(i); return i


def cmd_record_animation(a):
    run=run_path(a); p,h=get_handoff(run); i=upsert_anim(h,a.id)
    i.update({'status':a.status,'strategy':a.strategy or i.get('strategy'),'asset_uuid':a.asset_uuid or i.get('asset_uuid'),
              'runtime_object':a.runtime_object or i.get('runtime_object'),'frame_count':a.frame_count if a.frame_count is not None else i.get('frame_count'),'message':a.message})
    if a.readback_json: i['readback']=load(Path(a.readback_json).resolve())
    if h.get('animations') and all(x.get('status') in {'created','ready','skipped'} for x in h['animations']): h['status']='animations-ready'
    h['updated_at']=now(); save(p,h); sync_manifest(run,h); print(p); return 0


def cmd_record_runtime(a):
    run=run_path(a); p,h=get_handoff(run); r=h.setdefault('runtime_object',{})
    r.update({'status':a.status,'path':a.path or r.get('path'),'uuid':a.uuid or r.get('uuid')})
    if a.readback_json: r['readback']=load(Path(a.readback_json).resolve())
    elif a.status in {'created','ready'}: r['readback']={'status':'pass'}
    if a.status in {'created','ready'}: h['status']='runtime-ready'
    h['updated_at']=now(); save(p,h); sync_manifest(run,h); print(p); return 0


def cmd_record_preview(a):
    run=run_path(a); p,h=get_handoff(run)
    h['preview']={'status':a.status,'path':a.path,'instances':a.instances,'console_errors':a.console_errors,
                  'console_warnings':a.console_warnings,'note':a.note,'updated_at':now()}
    h['status']='integrated' if a.status=='pass' else 'preview-failed'; h['updated_at']=now()
    save(p,h); sync_manifest(run,h); print(p); return 0


def cmd_validate(a):
    run=run_path(a); _,h=get_handoff(run); errors=[]; warnings=[]
    imports=h.get('imports',[])
    if not imports: errors.append('engine import plan is empty')
    for i in imports:
        if i.get('status')!='imported': errors.append(f"asset not imported: {i.get('source')} ({i.get('status')})")
        if a.require_spriteframes and not i.get('spriteframe_uuid'): errors.append(f"missing SpriteFrame readback: {i.get('source')}")
    if a.require_animations:
        if not h.get('animations'): errors.append('no animations recorded')
        for i in h.get('animations',[]):
            if i.get('status') not in {'created','ready'}: errors.append(f"animation not ready: {i.get('id')} ({i.get('status')})")
    r=h.get('runtime_object',{})
    if a.require_runtime and r.get('status') not in {'created','ready'}: errors.append(f"runtime object not ready: {r.get('status')}")
    pv=h.get('preview',{})
    if a.require_preview:
        if pv.get('status')!='pass': errors.append(f"preview did not pass: {pv.get('status')}")
        if not pv.get('path'): errors.append('preview evidence path is empty')
        else:
            q=Path(pv['path']); q=q if q.is_absolute() else run/q
            if not q.exists(): errors.append(f'preview evidence file is missing: {q}')
        if pv.get('console_errors') not in {None,0}: errors.append(f"preview console errors: {pv.get('console_errors')}")
    report={'run':str(run),'ok':not errors,'errors':errors,'warnings':warnings}
    text=json.dumps(report,ensure_ascii=False,indent=2); print(text)
    if a.json_output: Path(a.json_output).write_text(text+'\n',encoding='utf-8')
    return 0 if not errors else 1


def cmd_status(a):
    run=run_path(a); p,h=get_handoff(run)
    print(json.dumps({'handoff':str(p),'status':h.get('status'),'adapter':h.get('adapter'),'adapter_tier':h.get('adapter_tier'),
                      'imports':h.get('imports'),'animations':h.get('animations'),'runtime_object':h.get('runtime_object'),'preview':h.get('preview')},ensure_ascii=False,indent=2))
    return 0


def parser():
    p=argparse.ArgumentParser(); s=p.add_subparsers(dest='command',required=True)
    x=s.add_parser('init'); x.add_argument('run_dir'); x.add_argument('--engine-type',default='engine-neutral'); x.add_argument('--adapter',default='auto'); x.add_argument('--adapter-tier',choices=('A','B','C')); x.add_argument('--from-final-assets',action='store_true'); x.add_argument('--asset',action='append',default=[]); x.add_argument('--target-root'); x.add_argument('--import-batch-size',type=int,default=4); x.add_argument('--import-timeout-seconds',type=int,default=30); x.add_argument('--import-max-retries',type=int,default=2); x.add_argument('--animation-strategy',choices=('auto','animation-clip','runtime-sequence'),default='auto'); x.add_argument('--allow-runtime-sequence-fallback',action=argparse.BooleanOptionalAction,default=True); x.add_argument('--force',action='store_true'); x.set_defaults(func=cmd_init)
    x=s.add_parser('set-adapter'); x.add_argument('run_dir'); x.add_argument('--adapter'); x.add_argument('--tier',choices=('A','B','C')); x.set_defaults(func=cmd_set_adapter)
    x=s.add_parser('next-batch'); x.add_argument('run_dir'); x.add_argument('--size',type=int); x.set_defaults(func=cmd_next_batch)
    x=s.add_parser('record-import'); x.add_argument('run_dir'); x.add_argument('--source',required=True); x.add_argument('--target'); x.add_argument('--status',required=True,choices=('pending','importing','imported','failed','timeout')); x.add_argument('--asset-uuid'); x.add_argument('--spriteframe-uuid'); x.add_argument('--message'); x.add_argument('--readback-json'); x.set_defaults(func=cmd_record_import)
    x=s.add_parser('record-animation'); x.add_argument('run_dir'); x.add_argument('--id',required=True); x.add_argument('--status',required=True,choices=('pending','created','ready','failed','skipped')); x.add_argument('--strategy',choices=('animation-clip','runtime-sequence')); x.add_argument('--asset-uuid'); x.add_argument('--runtime-object'); x.add_argument('--frame-count',type=int); x.add_argument('--message'); x.add_argument('--readback-json'); x.set_defaults(func=cmd_record_animation)
    x=s.add_parser('record-runtime'); x.add_argument('run_dir'); x.add_argument('--status',required=True,choices=('pending','created','ready','failed','skipped')); x.add_argument('--path'); x.add_argument('--uuid'); x.add_argument('--readback-json'); x.set_defaults(func=cmd_record_runtime)
    x=s.add_parser('record-preview'); x.add_argument('run_dir'); x.add_argument('--status',required=True,choices=('pending','pass','fail','blocked')); x.add_argument('--path'); x.add_argument('--instances',type=int,default=0); x.add_argument('--console-errors',type=int); x.add_argument('--console-warnings',type=int); x.add_argument('--note'); x.set_defaults(func=cmd_record_preview)
    x=s.add_parser('validate'); x.add_argument('run_dir'); x.add_argument('--require-spriteframes',action='store_true'); x.add_argument('--require-animations',action='store_true'); x.add_argument('--require-runtime',action='store_true'); x.add_argument('--require-preview',action='store_true'); x.add_argument('--json-output'); x.set_defaults(func=cmd_validate)
    x=s.add_parser('status'); x.add_argument('run_dir'); x.set_defaults(func=cmd_status)
    return p


if __name__ == '__main__':
    a=parser().parse_args(); raise SystemExit(a.func(a))
