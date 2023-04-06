import plotly.express as px
from dash import Dash, dcc, html
from skimage import data
from skimage import io

img = io.imread("page.png")
# img = data.chelsea()
fig = px.imshow(img)
fig.update_layout(dragmode="drawrect", height=2000)
config = {
    "modeBarButtonsToAdd": [
        "drawline",
        "drawopenpath",
        "drawclosedpath",
        "drawcircle",
        "drawrect",
        "eraseshape",
    ]
}

app = Dash(__name__)
app.layout = html.Div(
    [dcc.Graph(figure=fig, config=config)]
)

if __name__ == "__main__":
    app.run_server(debug=True)
