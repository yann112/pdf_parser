import fitz 
import json
import cv2
import ast
import pytesseract
import pandas as pd
import numpy as np
from pathlib import Path

class OcrTools:
    def __init__(self):
        self.working_dir = Path(__file__).parent
        pytesseract.pytesseract.tesseract_cmd = r'D:\soft\tesseract\tesseract.exe'
        
    @staticmethod
    def load_settings(path_to_settings:Path="settings.json"):
        with open(path_to_settings) as f:
            data = json.load(f)
            return data
        
    def _crop_part(self, original_image, x, y, w, h):
        result = original_image[y:y+h, x:x+w]
        return result

    @staticmethod
    def from_pdf_to_png(input_pdf_file, png_output_name="page.png"):
        pdf_file = fitz.open("pdf", input_pdf_file)
        #get first page
        page = pdf_file[0]
        png = page.get_pixmap(dpi=300)
        png.save(png_output_name)
        
    def build_df_from_template(self, str_dict_template:dict, template_mode:str="table"):
        # {'rows': {'row_1': (64, 240), 'row_2': (264, 205), 'row_3': (444, 181), 'row_4': (605, 205)}, 'columns': {'col_1': (94, 570), 'col_2': (574, 611), 'col_3': (1135, 575), 'col_4': (1675, 480)}}
        dict_template = ast.literal_eval(str_dict_template)
        df_output = pd.DataFrame(np.nan, index=range(len(dict_template['rows'].keys())), columns=dict_template['columns'].keys())
        if template_mode == "table":
            for index_col, col_name in enumerate(dict_template['columns'].keys()):
                list_col_temp = []
                for index_row, row_name in enumerate(dict_template['rows'].keys()):
                    str_guessed_text = self._guess_words_on_cell(
                        frame=cv2.imread(str(self.working_dir / "page.png")),
                        x=dict_template['columns'][col_name][0],
                        y=dict_template['rows'][row_name][0],
                        w=dict_template['columns'][col_name][1],
                        h=dict_template['rows'][row_name][1]
                        )
                    df_output.iloc[index_row, index_col] = str_guessed_text
        return df_output
                
    def _guess_words_on_cell(self, frame, x, y, w, h):
        croped_part = self._crop_part(frame,x,y,w,h)
        path_part_name = str(self.working_dir / "temp_cell.png")
        cv2.imwrite(path_part_name, croped_part)
        options = "--psm 12 -c tessedit_char_whitelist=0123456789azertyuiopqsdfghjklmwxcvbnAZERTYUIOPQSDFGHJKLMWXCVBN"
        str_croped_part_txt = pytesseract.image_to_string(path_part_name, config=options)
        return str_croped_part_txt

