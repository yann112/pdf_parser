# %%
import fitz 
import pytesseract
import cv2
import pandas as pd
from pathlib import Path
import imutils
import numpy as np

#first install the tesseract executable
#PATH to tesseract executable:
pytesseract.pytesseract.tesseract_cmd = r'D:\soft\tesseract\tesseract.exe'
# file path you want to extract images from

file = Path("D:/2022_12_15_pdf_parsing/2023_04_05_demande_carine_P/liste_des_modules4_concernés.pdf")
parent_dir = file.parent
def crop_part(original_image, x, y, w, h):
    result = original_image[y:y+h, x:x+w]
    return result

def from_pdf_to_png(input_pdf_file, png_output_name):
    pdf_file = fitz.open(input_pdf_file)
    #get first page
    page = pdf_file[0]
    png = page.get_pixmap(dpi=300)
    png.save(parent_dir / png_output_name)

def enhance_img(png_output_name):
    img =cv2.imread(png_output_name)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
    # apply a distance transform which calculates the distance to the
    # closest zero pixel for each pixel in the input image
    dist = cv2.distanceTransform(thresh, cv2.DIST_L2, 5)
    # normalize the distance transform such that the distances lie in
    # the range [0, 1] and then convert the distance transform back to
    # an unsigned 8-bit integer in the range [0, 255]
    dist = cv2.normalize(dist, dist, 0, 1.0, cv2.NORM_MINMAX)
    dist = (dist * 255).astype("uint8")
    # threshold the distance transform using Otsu's method
    dist = cv2.threshold(dist, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
    kernel = np.ones((2,2),np.uint8)
    opening = cv2.morphologyEx(dist, cv2.MORPH_OPEN, kernel)

    # find contours in the opening image, then initialize the list of
    # contours which belong to actual characters that we will be OCR'ing
    cnts = cv2.findContours(opening.copy(), cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    list_mask = []
    # loop over the contours
    for c in cnts:
        # compute the bounding box of the contour
        (x, y, w, h) = cv2.boundingRect(c)
        # check if contour is at least 5px wide and 5px tall, and if
        # so, consider the contour a digit
        if w >= 5 and h >= 5:
            hull = cv2.convexHull(c)
            mask = np.zeros(img.shape[:2], dtype="uint8")
            cv2.drawContours(mask, [hull], -1, 255, -1)
            mask = cv2.dilate(mask, None, iterations=3)
            list_mask.append(mask)
    mask = 255 * sum(list_mask)
    mask = mask.clip(0, 255).astype("uint8")
     
    # take the bitwise of the opening image and the mask to reveal *just*
    # the characters in the image
    final = cv2.bitwise_and(opening, opening, mask=mask)
    
    cv2.imwrite(str(parent_dir / png_output_name), final)

def get_pandas_serie_from_part(frame,x,y,w,h,output_name):
    croped_part = crop_part(frame,x,y,w,h)
    path_part_name = str(parent_dir / f"{output_name}.png")
    cv2.imwrite(path_part_name, croped_part)
    options = "--psm 12 -c tessedit_char_whitelist=0123456789azertyuiopqsdfghjklmwxcvbnAZERTYUIOPQSDFGHJKLMWXCVBN"
    croped_part_txt = pytesseract.image_to_string(path_part_name, config=options)
    serie_croped_part = pd.Series(croped_part_txt.split("\n"), name=output_name)
    return serie_croped_part
    
def main(file):    
    from_pdf_to_png(file, "page.png")
    png_output_name = str(parent_dir / "page.png")
    
    enhance_img(png_output_name)
    frame = cv2.imread(png_output_name)
    header = get_pandas_serie_from_part(frame,x=920,y=318,w=820,h=100,output_name="header")
    col1 = get_pandas_serie_from_part(frame,x=325,y=680,w=255,h=2010,output_name="NS_ensemble_Roue_TL_1")
    col2 = get_pandas_serie_from_part(frame,x=578,y=680,w=200,h=2010,output_name="NS_module_M04_1")
    col3 = get_pandas_serie_from_part(frame,x=795,y=680,w=195,h=2010,output_name="NS_moteur_1")
    col4 = get_pandas_serie_from_part(frame,x=1036,y=680,w=235,h=2010,output_name="NS_ensemble_Roue_TL_2")
    col5 = get_pandas_serie_from_part(frame,x=1260,y=680,w=200,h=2010,output_name="NS_module_M04_2")
    col6 = get_pandas_serie_from_part(frame,x=1477,y=680,w=200,h=2010,output_name="NS_moteur_2")
    col7 = get_pandas_serie_from_part(frame,x=1709,y=680,w=235,h=2010,output_name="NS_ensemble_Roue_TL_3")
    col8 = get_pandas_serie_from_part(frame,x=1996,y=680,w=180,h=2010,output_name="NS_module_M04_3")
    col9 = get_pandas_serie_from_part(frame,x=2170,y=680,w=200,h=2010,output_name="NS_moteur_3")    
    
    df_data = pd.concat([col1, col2, col3, col4, col5, col6, col7, col8, col9], ignore_index=True, axis=1)
    df_data.columns = [
        'NS_ensemble_Roue_TL_1', 'NS_module_M04_1', 'NS_moteur_1',
        'NS_ensemble_Roue_TL_2', 'NS_module_M04_2', 'NS_moteur_2',
        'NS_ensemble_Roue_TL_3', 'NS_module_M04_3', 'NS_moteur_3',
        ]
    return (header, df_data)

header, df_data = main(file)
header.to_csv(parent_dir / 'header.csv', sep=';', index=False)
df_data.to_csv(parent_dir / 'df_data.csv', sep=';', index=False)

# %%
