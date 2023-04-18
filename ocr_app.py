import plotly.express as px
from dash import Dash, dcc, html, Input, Output, State, no_update
from skimage import data
import cv2
import base64
from ocr_tools import OcrTools 
from pathlib import Path

WORKING_DIR = Path(__file__).parent

app = Dash(__name__)
app.layout = html.Div([
        dcc.Upload(
        id='upload-data',
        children=html.Div([
            'Drag and Drop or ',
            html.A('Select PDF Files')
        ]),
        style={
            'width': '100%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px'
        },
        multiple=False
    ),
        html.Div(id='filename'),
        html.Button('Save template', id='save_template', n_clicks=0),
        dcc.Graph(id='graph',figure=px.imshow(data.chelsea()), style={'height': '90vh'}),
        html.Div(id='content')
    ])

@app.callback(
    Output('filename', 'children'),
    Input('upload-data', 'filename'))
def print_filename(filename):
    return f"input_file : {filename}"

@app.callback(
    [
    Output('graph', 'figure'),
    Output('graph', 'config'),
    ],
    Input('upload-data', 'contents'),
    State('upload-data', 'filename'))
def print_image(contents, filename):
    global WORKING_DIR
    
    layout = {
        'dragmode' : 'drawrect',
        'newshape' : {'line': {'color': 'red', 'width': 2}}
    }
    config = {
    "modeBarButtonsToAdd": [
        "drawrect",
        "eraseshape",
    ],
    'displaylogo': False
    }
    if contents != None :
        content_type, content_string = contents.split(',')
        if "pdf" in content_type:
            input_pdf_file = base64.b64decode(content_string)
            OcrTools.from_pdf_to_png(input_pdf_file, png_output_name=WORKING_DIR/"page.png")
            img = cv2.imread(str(WORKING_DIR/"page.png"))
            new_fig = px.imshow(img)
            new_fig['layout'].update(layout)
            
            return new_fig, config
        else : 
            return no_update, no_update  
    else:
        return no_update, no_update

@app.callback(
    Output('content', 'children'),
    Input('graph', 'relayoutData'))
def add_shape(fig_data):
    if fig_data == None:
        return
    if 'shapes' in fig_data:
        dict_shapes = {"rows":{}, "columns":{}}
        index_row = 1
        index_col = 1
        for index_shapes, shapes_data in enumerate(fig_data['shapes']):
            x_0 = int(fig_data['shapes'][index_shapes]['x0'])
            y_0 = int(fig_data['shapes'][index_shapes]['y0'])
            w = int(fig_data['shapes'][index_shapes]['x1']) - x_0
            h = int(fig_data['shapes'][index_shapes]['y1']) - y_0
            if w>h:       
                dict_shapes['rows'][f"row_{index_row}"] = (y_0, h)
                index_row += 1   
            else:
                dict_shapes['columns'][f"col_{index_col}"] = (x_0, w)
                index_col += 1
                
        return f"{dict_shapes}"
    else :
        pass

if __name__ == "__main__":
    app.run_server(debug=True)
