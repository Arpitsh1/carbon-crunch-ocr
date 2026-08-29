import json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
from src.pipeline import process
from src.summary import build_summary
root=Path('data/input'); out=Path('outputs/json'); out.mkdir(exist_ok=True)
files=sorted([*root.glob('*.jpg'),*root.glob('*.jpeg'),*root.glob('*.png')])
missing=[f for f in files if not (out/(f.stem+'.json')).exists()]
print('missing',len(missing))
for i,f in enumerate(missing,1):
 try:
  r=process(f); (out/(f.stem+'.json')).write_text(json.dumps(r,indent=2,ensure_ascii=False)); print(f'[{i}/{len(missing)}] {f.name}: {r["store_name"]["value"]} | {r["total_amount"]["value"]}')
 except Exception as e: print('ERROR',f,e,file=sys.stderr)
results=[json.loads(p.read_text()) for p in out.glob('*.json')]
summary=build_summary(results)
Path('outputs/expense_summary.json').write_text(json.dumps(summary,indent=2))
Path('outputs/all_results.json').write_text(json.dumps(results,indent=2,ensure_ascii=False))
print(json.dumps(summary,indent=2))
