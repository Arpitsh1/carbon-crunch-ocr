import json,sys,os
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor,as_completed
sys.path.insert(0,str(Path(__file__).parent))
from src.pipeline import process
from src.summary import build_summary
root=Path('data/input'); out=Path('outputs/json'); out.mkdir(exist_ok=True)
files=sorted([*root.glob('*.jpg'),*root.glob('*.jpeg'),*root.glob('*.png')])
missing=[str(f) for f in files if not (out/(f.stem+'.json')).exists()]
print('missing',len(missing),flush=True)
def worker(s):
 f=Path(s); r=process(f); (out/(f.stem+'.json')).write_text(json.dumps(r,indent=2,ensure_ascii=False)); return f.name,r['store_name']['value'],r['total_amount']['value']
with ProcessPoolExecutor(max_workers=4) as ex:
 futs=[ex.submit(worker,f) for f in missing]
 for i,fut in enumerate(as_completed(futs),1):
  try: print(f'[{i}/{len(missing)}]',fut.result(),flush=True)
  except Exception as e: print('ERR',e,flush=True)
results=[json.loads(p.read_text()) for p in out.glob('*.json') if p.name not in ('expense_summary.json','all_results.json')]
summary=build_summary(results)
Path('outputs/expense_summary.json').write_text(json.dumps(summary,indent=2)); Path('outputs/all_results.json').write_text(json.dumps(results,indent=2,ensure_ascii=False))
print('SUMMARY',json.dumps(summary,indent=2),flush=True)
