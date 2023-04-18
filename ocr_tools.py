import fitz 
import json
from pathlib import Path

class OcrTools:
    def __init__(self):
        pass
    
    @staticmethod
    def load_settings(path_to_settings:Path="settings.json"):
        with open(path_to_settings) as f:
            data = json.load(f)
            return data
    @staticmethod
    def from_pdf_to_png(input_pdf_file, png_output_name="page.png"):
        pdf_file = fitz.open("pdf", input_pdf_file)
        #get first page
        page = pdf_file[0]
        png = page.get_pixmap(dpi=300)
        png.save(png_output_name)