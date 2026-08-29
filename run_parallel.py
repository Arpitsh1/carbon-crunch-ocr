import argparse, json, sys, os
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed
from src.pipeline import process_image, save_result
from src.summary import build_summary

def one(p):
    return process_image(p)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--input',default='data/input'); ap.add_argument('--output',default='outputs/json')
    ap.add_argument('--summary',default='outputs/expense_summary.json'); ap.add_argument('--workers',type=int,default=max(2,min(8,os.cpu_count() or 2)))
    a=ap.parse_args(); paths=sorted([p for p in Path(a.input).rglob('*') if p.suffix.lower() in {'.jpg','.jpeg','.png','.webp'}])
    Path(a.output).mkdir(parents=True,exist_ok=True); records=[]
    with ProcessPoolExecutor(max_workers=a.workers) as ex:
        futs={ex.submit(one,p):p for p in paths}
        for i,f in enumerate(as_completed(futs),1):
            p=futs[f]
            try:
                r=f.result(); save_result(r,a.output); records.append(r)
                print(f'[{i}/{len(paths)}] {p.name}: total={r["total_amount"]["value"]} conf={r["total_amount"]["confidence"]:.2f}',flush=True)
            except Exception as e: print(f'[ERROR] {p.name}: {e}',file=sys.stderr,flush=True)
    Path(a.summary).write_text(json.dumps(build_summary(records),indent=2),encoding='utf-8')
    print(json.dumps(build_summary(records),indent=2))
if __name__=='__main__': main()
