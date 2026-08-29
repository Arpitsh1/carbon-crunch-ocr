import argparse,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
from src.pipeline import process
from src.summary import build_summary

p=argparse.ArgumentParser(); p.add_argument('--input',default='data/input'); p.add_argument('--output',default='outputs/json'); args=p.parse_args()
root=Path(args.input); out=Path(args.output); out.mkdir(parents=True,exist_ok=True)
files=sorted([*root.glob('*.jpg'),*root.glob('*.jpeg'),*root.glob('*.png')])
results=[]
for i,f in enumerate(files,1):
    try:
        r=process(f); results.append(r)
        (out/(f.stem+'.json')).write_text(json.dumps(r,indent=2,ensure_ascii=False))
        print(f'[{i}/{len(files)}] {f.name}: {r["store_name"]["value"]} | total={r["total_amount"]["value"]} | conf={r["total_amount"]["confidence"]}')
    except Exception as e: print(f'ERROR {f}: {e}',file=sys.stderr)
summary=build_summary(results)
Path('outputs/expense_summary.json').write_text(json.dumps(summary,indent=2))
Path('outputs/all_results.json').write_text(json.dumps(results,indent=2,ensure_ascii=False))
print('SUMMARY',json.dumps(summary,indent=2))
