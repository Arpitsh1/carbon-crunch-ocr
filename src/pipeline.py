import json,sys
from pathlib import Path
from .preprocessing import preprocess_image
from .ocr_engine import run_ocr
from .extraction import extract_fields


def process(path):
    imgs=preprocess_image(path)
    best,_=run_ocr(imgs)
    result=extract_fields(best['text'],best['ocr_confidence'])
    result['source_file']=Path(path).name
    result['ocr']={'confidence':round(best['ocr_confidence'],3),'preprocessing_variant':best['variant'],'deskew_angle':round(imgs['deskew_angle'],2),'raw_text':best['text']}
    return result
