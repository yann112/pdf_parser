# %%
import fitz 
import pytesseract
import cv2
import pandas as pd

#first install the tesseract executable
#PATH to tesseract executable:
pytesseract.pytesseract.tesseract_cmd = r'D:\soft\tesseract\tesseract.exe'
# file path you want to extract images from
file = "Annexe C.pdf"

def crop_part(original_image, x, y, w, h):
    result = original_image[y:y+h, x:x+w]
    return result

def from_pdf_to_png(input_pdf_file, png_output_name):
    pdf_file = fitz.open(input_pdf_file)
    #get first page
    page = pdf_file[0]
    png = page.get_pixmap(dpi=300)
    png.save(png_output_name)

def get_pandas_serie_from_part(frame,x,y,w,h,output_name):
    croped_part = crop_part(frame,x,y,w,h)
    cv2.imwrite(f"{output_name}.png", croped_part)
    croped_part_txt = pytesseract.image_to_string(f"{output_name}.png")
    serie_croped_part = pd.Series(croped_part_txt.split("\n"), name=output_name)
    return serie_croped_part
    
def main(file):    
    from_pdf_to_png(file, "page.png")
    frame = cv2.imread("page.png")
    header = get_pandas_serie_from_part(frame,x=100,y=500,w=1500,h=80,output_name="header")
    col1 = get_pandas_serie_from_part(frame,x=0,y=800,w=1000,h=2100,output_name="designation")
    col2 = get_pandas_serie_from_part(frame,x=770,y=800,w=920,h=2100,output_name="identity")
    col3 = get_pandas_serie_from_part(frame,x=1550,y=800,w=400,h=2100,output_name="reference")
    col4 = get_pandas_serie_from_part(frame,x=1950,y=800,w=500,h=2100,output_name="sn")
    df_data = pd.concat([col1, col2, col3, col4], ignore_index=True, axis=1)
    df_data.columns = ['designation', 'identity', 'reference', 'sn']
    return (header, df_data)

header, df_data = main(file)
header.to_csv('header.csv', sep=';', index=False)
df_data.to_csv('df_data.csv', sep=';', index=False)

# %%
