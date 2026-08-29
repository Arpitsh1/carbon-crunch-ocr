import cv2, numpy as np


def resize_for_ocr(img, target_width=400, target_height=1000):
    h,w=img.shape[:2]
    scale=min(target_width/w, target_height/h, 1.0)
    if scale < 1.0:
        return cv2.resize(img,(max(1,int(w*scale)),max(1,int(h*scale))),interpolation=cv2.INTER_AREA)
    return img


def estimate_skew(gray):
    bw=cv2.threshold(gray,0,255,cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)[1]
    coords=np.column_stack(np.where(bw>0))
    if len(coords)<100: return 0.0
    # use minAreaRect on a subsample to avoid huge memory
    if len(coords)>50000: coords=coords[np.random.default_rng(0).choice(len(coords),50000,replace=False)]
    angle=cv2.minAreaRect(coords.astype(np.float32))[-1]
    if angle < -45: angle += 90
    if angle > 45: angle -= 90
    return float(angle)


def deskew(gray):
    angle=estimate_skew(gray)
    if abs(angle)<0.4: return gray, angle
    h,w=gray.shape[:2]; center=(w//2,h//2)
    M=cv2.getRotationMatrix2D(center,angle,1.0)
    return cv2.warpAffine(gray,M,(w,h),flags=cv2.INTER_CUBIC,borderMode=cv2.BORDER_REPLICATE),angle


def preprocess_image(path):
    img=cv2.imread(str(path))
    if img is None: raise ValueError(f'Unable to read image: {path}')
    img=resize_for_ocr(img)
    gray=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    gray,angle=deskew(gray)
    den=cv2.fastNlMeansDenoising(gray,None,h=10,templateWindowSize=7,searchWindowSize=21)
    clahe=cv2.createCLAHE(clipLimit=2.0,tileGridSize=(8,8))
    enhanced=clahe.apply(den)
    # Keep grayscale as primary because many receipts are already clean.
    adaptive=cv2.adaptiveThreshold(enhanced,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY,31,11)
    return {'gray':gray,'enhanced':enhanced,'adaptive':adaptive,'deskew_angle':angle}
