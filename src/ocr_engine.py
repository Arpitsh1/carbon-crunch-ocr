import os
os.environ.setdefault('OMP_THREAD_LIMIT','1')
import pytesseract, pandas as pd, re
from pytesseract import Output

CONFIGS=['--oem 3 --psm 6']

def run_ocr(images):
    candidates=[]
    for name,img in images.items():
        if name=='deskew_angle': continue
        df=pytesseract.image_to_data(img,config=CONFIGS[0],output_type=Output.DATAFRAME)
        df=df.dropna(subset=['text']).copy()
        df['text']=df['text'].astype(str).str.strip()
        df=df[df.text!='']
        conf=pd.to_numeric(df['conf'],errors='coerce')
        mean_conf=float(conf[conf>=0].mean()/100) if (conf>=0).any() else 0.0
        text='\n'.join(df.groupby(['block_num','par_num','line_num'])['text'].apply(lambda x:' '.join(x)).tolist())
        candidates.append({'variant':name,'df':df,'text':text,'ocr_confidence':max(0,min(1,mean_conf))})
    # Favor confidence, but lightly prefer enhanced over thresholded when close.
    candidates.sort(key=lambda x:(x['ocr_confidence'] + (0.015 if x['variant']=='enhanced' else 0)),reverse=True)
    return candidates[0],candidates
