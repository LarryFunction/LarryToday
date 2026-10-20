"""Immutable editions and explicit, additive corrections."""
import json
import hashlib
import os
from datetime import datetime,timezone

def immutable_json(path,value):
    from scripts.update_news import atomic_json
    path.parent.mkdir(parents=True,exist_ok=True)
    # Write a complete staging file, then hard-link without replacing existing bytes.
    import tempfile
    fd,tmp=tempfile.mkstemp(dir=path.parent,suffix='.tmp')
    try:
        with os.fdopen(fd,'w',encoding='utf-8') as f: json.dump(value,f,ensure_ascii=False,indent=2)
        if os.name=='nt': os.rename(tmp,path)  # Windows rename fails if destination exists.
        else: os.link(tmp,path)
    finally:
        if os.path.exists(tmp): os.unlink(tmp)

def save(data, edition, note=None):
    from scripts.update_news import atomic_json
    # Archive voices with the edition so later collection cannot rewrite history.
    if 'social_posts' not in edition:
        from scripts.editorial import timestamp
        bounds=edition.get('window',{})
        start,end=timestamp(bounds.get('start')),timestamp(bounds.get('end'))
        path=data/'social-posts.json'
        posts=json.loads(path.read_text(encoding='utf-8')) if path.exists() else []
        edition['social_posts']=[p for p in posts if start and end and (t:=timestamp(p.get('published_at'))) and start<=t<end]
    day=edition['date']; canonical=data/'editions'/f'{day}.json'
    revision_dir=data/'revisions'/day
    history_file=revision_dir/'index.json'
    history=json.loads(history_file.read_text(encoding='utf-8')) if history_file.exists() else []
    if canonical.exists():
        if not note or not note.strip(): raise ValueError('该期已发布。更新须提供 --revision-note；初版永久保留')
        if not history:
            old=json.loads(canonical.read_text(encoding='utf-8'))
            if not (revision_dir/'1.json').exists(): immutable_json(revision_dir/'1.json',old)
            history=[{'revision':1,'published_at':old.get('updated_at'),'note':'初版（历史版本迁移）'}]
    revision=max([int(p.stem) for p in revision_dir.glob('*.json') if p.stem.isdigit()]+[0])+1
    edition.update(revision=revision,revision_note=note.strip() if note else '首次出版',published_at=datetime.now(timezone.utc).isoformat())
    edition['content_hash']=hashlib.sha256(json.dumps(edition,sort_keys=True,ensure_ascii=False).encode()).hexdigest()
    immutable_json(revision_dir/f'{revision}.json',edition)
    history.append({'revision':revision,'published_at':edition['published_at'],'note':edition['revision_note'],'content_hash':edition['content_hash']})
    atomic_json(history_file,history)
    if not canonical.exists(): immutable_json(canonical,edition)
    # latest.json is a replaceable reading pointer; every published payload above is immutable.
    current=json.loads((data/'latest.json').read_text(encoding='utf-8')) if (data/'latest.json').exists() else {}
    if current.get('date','')<=day: atomic_json(data/'latest.json',edition)
    atomic_json(data/'archive.json',sorted([p.stem for p in (data/'editions').glob('????-??-??.json')],reverse=True))
    return revision
