import dash
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
import matplotlib

matplotlib.use("Agg")
import dash_bootstrap_components as dbc
from dash import dcc, html
from dash.dependencies import Input, Output, State
from dash import dash_table
import matplotlib.pyplot as plt
import io
import base64
import plotly.graph_objs as go
import dash_daq as daq


app = dash.Dash(
    __name__,
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
    external_stylesheets=[dbc.themes.BOOTSTRAP],
)
app.title = "Ambient Noise Dashboard"

server = app.server
app.config.suppress_callback_exceptions = True


# %% Create map figure
lats = np.random.uniform(low=25, high=49, size=100)
lons = np.random.uniform(low=-125, high=-67, size=100)

fig = go.Figure(
    go.Scattermapbox(
        name="Channels",
        lat=lats,
        lon=lons,
        mode="markers",
        marker=go.scattermapbox.Marker(size=5, color="red"),
        text=["Point " + str(i + 1) + ": red" for i in range(100)],
    )
)

# Set mapbox style and center the map on the US
mapbox_center = go.layout.mapbox.Center(lat=37.0902, lon=-95.7129)
mapbox_zoom = 1
fig.update_layout(
    mapbox_style="stamen-terrain",  # "open-street-map",
    mapbox_center=mapbox_center,
    mapbox_zoom=mapbox_zoom,
    showlegend=True,  # 将showlegend属性设置为True
    legend=dict(
        yanchor="top",
        y=0.99,
        xanchor="left",
        x=0.01,
        bgcolor="rgba(0,0,0,0)",
        bordercolor="rgba(0,0,0,0)",
        borderwidth=1,
        font=dict(
            family="sans-serif",
            size=15,
            color="black",
        ),
    ),
)


# %% Matplotlib
def generate_figure():
    plt.close("all")
    fig, ax = plt.subplots()
    data = np.random.normal(size=100)
    ax.hist(data, bins=20)
    return fig


def encode_image(fig):
    buffer = io.BytesIO()
    fig.savefig(buffer, format="svg", dpi=100)
    buffer.seek(0)
    img_str = buffer.read().decode("utf-8")
    encoded_image = "data:image/svg+xml;base64," + base64.b64encode(
        img_str.encode("utf-8")
    ).decode("utf-8")
    image = html.Img(
        src=encoded_image, alt="图像标题", style={"width": "100%", "height": "auto"}
    )

    return image


# %% left panel
def description_card():
    """
    :return: A Div containing dashboard title & descriptions.
    """
    div = html.Div(
        id="description-card",
        children=[
            # html.H5("Ambient Noise"),
            html.H3(
                "Welcome to real-time ambient noise dashboard",
                style={"color": "#363737", "font-weight": "bold", "font-size": "3rem"},
            ),
            html.Div(
                id="intro",
                children="Explore different visualization parameters. Hover on the 'map' and 'waveform' panel to check the channel information.",
            ),
        ],
    )

    return div


plot_list = [
    "parameters",
    "map",
    "waveform",
    "spectrogram",
    "stack",
    "beamforming",
    "ppsd",
]


def select_plot():
    """
    :return: A Div containing dashboard title & descriptions.
    """
    div = html.Div(
        id="control-card",
        style={"width": "100%", "display": "inline-block", "vertical-align": "top"},
        children=[
            html.P("Select Plot"),
            dcc.Dropdown(
                id="select-plot",
                options=[{"label": i, "value": i} for i in plot_list],
                value=plot_list[:],
                multi=True,
            ),
            html.Br(),
        ],
    )

    return div


def map_mode():
    """
    :return: A Div containing dashboard title & descriptions.
    """
    div = html.Div(
        id="control-card",
        style={"width": "100%", "display": "inline-block", "vertical-align": "top"},
        children=[
            html.P("Map Mode"),
            dcc.Dropdown(
                options=[
                    "basic",
                    "streets",
                    "outdoors",
                    "light",
                    "dark",
                    "satellite",
                    "satellite-streets",
                    "navigation-preview-day",
                    "navigation-preview-night",
                    "navigation-guidance-day",
                    "navigation-guidance-night",
                    "terrain",
                    "terrain-streets",
                    "stamen-toner",
                    "stamen-terrain",
                    "stamen-watercolor",
                    "carto-positron",
                    "carto-darkmatter",
                ],
                value="stamen-terrain",
            ),
            html.Br(),
        ],
    )

    return div


def waveform_panel():
    div = html.Div(
        id="control-card",
        style={"width": "100%", "display": "inline-block", "vertical-align": "top"},
        children=[
            html.P("Waveform"),
            html.Div(
                id="control-card",
                style={
                    "width": "100%",
                    "display": "inline-block",
                    "vertical-align": "top",
                },
                children=[
                    html.Div("- Time Window:"),
                    dcc.Input(
                        id="waveform-time-length",
                        type="number",
                        placeholder="second (s)",
                        debounce=True,
                        value=20,
                        style={
                            "width": "120px",
                            "height": "20px",
                            "margin-left": "15px",
                        },
                    ),
                    html.Div("- Detrend:"),
                    dcc.RadioItems(
                        options=["on", "off"],
                        value="on",
                        id="crossfilter-xaxis-type",
                        style={"width": "100%"},
                        labelStyle={"marginLeft": "15px"},
                    ),
                    html.Div("- Taper:"),
                    dcc.RadioItems(
                        options=["on", "off"],
                        value="on",
                        id="crossfilter-xaxis-type",
                        style={"width": "100%"},
                        labelStyle={"marginLeft": "15px"},
                    ),
                    html.Div("- Bandpass:"),
                    dcc.Input(
                        id="input1",
                        type="number",
                        placeholder="freqmin (hz)",
                        debounce=True,
                        value=20,
                        style={
                            "width": "120px",
                            "height": "20px",
                            "margin-left": "15px",
                        },
                    ),
                    dcc.Input(
                        id="input2",
                        type="number",
                        placeholder="freqmax (hz)",
                        debounce=True,
                        value=20,
                        style={
                            "width": "120px",
                            "height": "20px",
                            "margin-left": "15px",
                        },
                    ),
                    html.Div(id="output"),
                ],
            ),
            html.Br(),
            html.Br(),
        ],
    )

    return div


def spectrogram_panel():
    div = html.Div(
        id="control-card",
        style={"width": "100%", "display": "inline-block", "vertical-align": "top"},
        children=[
            html.P("Spectrogram"),
            html.Div(
                id="control-card",
                style={
                    "width": "100%",
                    "display": "inline-block",
                    "vertical-align": "top",
                },
                children=[
                    html.Div("- Time Window:"),
                    dcc.Input(
                        id="waveform-time-length",
                        type="number",
                        placeholder="second (s)",
                        debounce=True,
                        value=20,
                        style={
                            "width": "120px",
                            "height": "20px",
                            "margin-left": "15px",
                        },
                    ),
                    html.Div("- Channel:"),
                    dcc.Input(
                        id="waveform-time-length",
                        type="number",
                        placeholder="index",
                        debounce=True,
                        value=20,
                        min=1,
                        max=100,
                        step=1,
                        style={
                            "width": "120px",
                            "height": "20px",
                            "margin-left": "15px",
                        },
                    ),
                    html.Div("- Dbscale:"),
                    dcc.RadioItems(
                        options=["on", "off"],
                        value="on",
                        id="crossfilter-xaxis-type",
                        style={"width": "100%"},
                        labelStyle={"marginLeft": "15px"},
                    ),
                    html.Div("- Log:"),
                    dcc.RadioItems(
                        options=["on", "off"],
                        value="on",
                        id="crossfilter-xaxis-type",
                        style={"width": "100%"},
                        labelStyle={"marginLeft": "15px"},
                    ),
                ],
            ),
            html.Br(),
            html.Br(),
        ],
    )

    return div


def stack_panel():
    div = html.Div(
        id="control-card",
        style={"width": "100%", "display": "inline-block", "vertical-align": "top"},
        children=[
            html.P("Stack"),
            html.Div(
                id="control-card",
                style={
                    "width": "100%",
                    "display": "inline-block",
                    "vertical-align": "top",
                },
                children=[
                    html.Div("- Pair Index:"),
                    dcc.Input(
                        id="waveform-time-length",
                        type="number",
                        placeholder="source index",
                        debounce=True,
                        value=20,
                        min=1,
                        max=100,
                        step=1,
                        style={
                            "width": "120px",
                            "height": "20px",
                            "margin-left": "15px",
                        },
                    ),
                    dcc.Input(
                        id="waveform-time-length",
                        type="number",
                        placeholder="receiver index",
                        debounce=True,
                        value=20,
                        min=1,
                        max=100,
                        step=1,
                        style={
                            "width": "120px",
                            "height": "20px",
                            "margin-left": "15px",
                        },
                    ),
                    html.Div("- Time Window:"),
                    dcc.Input(
                        id="waveform-time-length",
                        type="number",
                        placeholder="second (s)",
                        debounce=True,
                        value=20,
                        style={
                            "width": "120px",
                            "height": "20px",
                            "margin-left": "15px",
                        },
                    ),
                    html.Div("- Window Interval:"),
                    dcc.Input(
                        id="waveform-time-length",
                        type="number",
                        placeholder="second (s)",
                        debounce=True,
                        value=20,
                        style={
                            "width": "120px",
                            "height": "20px",
                            "margin-left": "15px",
                        },
                    ),
                    html.Div("- Lag Window:"),
                    dcc.Input(
                        id="waveform-time-length",
                        type="number",
                        placeholder="lag start (s)",
                        debounce=True,
                        value=20,
                        style={
                            "width": "120px",
                            "height": "20px",
                            "margin-left": "15px",
                        },
                    ),
                    dcc.Input(
                        id="waveform-time-length",
                        type="number",
                        placeholder="lag end (s)",
                        debounce=True,
                        value=20,
                        style={
                            "width": "120px",
                            "height": "20px",
                            "margin-left": "15px",
                        },
                    ),
                    html.Div("- Amp Normalize:"),
                    dcc.RadioItems(
                        options=["on", "off"],
                        value="on",
                        id="crossfilter-xaxis-type",
                        style={"width": "100%"},
                        labelStyle={"marginLeft": "15px"},
                    ),
                    html.Div("- Amp Scale:"),
                    dcc.Input(
                        id="waveform-time-length",
                        type="number",
                        placeholder="amp scale",
                        debounce=True,
                        value=1,
                        style={
                            "width": "120px",
                            "height": "20px",
                            "margin-left": "15px",
                        },
                    ),
                    html.Div("- Yticklabel Num:"),
                    dcc.Input(
                        id="waveform-time-length",
                        type="number",
                        placeholder="second (s)",
                        debounce=True,
                        value=20,
                        style={
                            "width": "120px",
                            "height": "20px",
                            "margin-left": "15px",
                        },
                    ),
                    html.Div("- Bandpass:"),
                    dcc.Input(
                        id="input1",
                        type="number",
                        placeholder="freqmin (hz)",
                        debounce=True,
                        value=20,
                        style={
                            "width": "120px",
                            "height": "20px",
                            "margin-left": "15px",
                        },
                    ),
                    dcc.Input(
                        id="input2",
                        type="number",
                        placeholder="freqmax (hz)",
                        debounce=True,
                        value=20,
                        style={
                            "width": "120px",
                            "height": "20px",
                            "margin-left": "15px",
                        },
                    ),
                    html.Div(id="output"),
                ],
            ),
            html.Br(),
            html.Br(),
        ],
    )

    return div


def moveout_panel():
    div = html.Div(
        id="control-card",
        style={"width": "100%", "display": "inline-block", "vertical-align": "top"},
        children=[
            html.P("Moveout"),
            html.Div(
                id="control-card",
                style={
                    "width": "100%",
                    "display": "inline-block",
                    "vertical-align": "top",
                },
                children=[
                    html.Div("- Source Index:"),
                    dcc.Input(
                        id="waveform-time-length",
                        type="number",
                        placeholder="source index",
                        debounce=True,
                        value=20,
                        min=1,
                        max=100,
                        step=1,
                        style={
                            "width": "120px",
                            "height": "20px",
                            "margin-left": "15px",
                        },
                    ),
                    dcc.Input(
                        id="waveform-time-length",
                        type="number",
                        placeholder="receiver index",
                        debounce=True,
                        value=20,
                        min=1,
                        max=100,
                        step=1,
                        style={
                            "width": "120px",
                            "height": "20px",
                            "margin-left": "15px",
                        },
                    ),
                    html.Div("- Unit:"),
                    dcc.RadioItems(
                        id="waveform-time-length",
                        options=["m", "km", "deg"],
                        value="m",
                        style={"width": "100%"},
                        labelStyle={"marginLeft": "15px"},
                    ),
                    html.Div("- Dist Interval:"),
                    dcc.Input(
                        id="waveform-time-length",
                        type="number",
                        placeholder="distance (unit)",
                        debounce=True,
                        value=20,
                        style={
                            "width": "120px",
                            "height": "20px",
                            "margin-left": "15px",
                        },
                    ),
                    html.Div("- Dist Window:"),
                    dcc.Input(
                        id="waveform-time-length",
                        type="number",
                        placeholder="distance (unit)",
                        debounce=True,
                        value=20,
                        style={
                            "width": "120px",
                            "height": "20px",
                            "margin-left": "15px",
                        },
                    ),
                    dcc.Input(
                        id="waveform-time-length",
                        type="number",
                        placeholder="distance (unit)",
                        debounce=True,
                        value=20,
                        style={
                            "width": "120px",
                            "height": "20px",
                            "margin-left": "15px",
                        },
                    ),
                    html.Div("- Lag Window:"),
                    dcc.Input(
                        id="waveform-time-length",
                        type="number",
                        placeholder="lag start (s)",
                        debounce=True,
                        value=20,
                        style={
                            "width": "120px",
                            "height": "20px",
                            "margin-left": "15px",
                        },
                    ),
                    dcc.Input(
                        id="waveform-time-length",
                        type="number",
                        placeholder="lag end (s)",
                        debounce=True,
                        value=20,
                        style={
                            "width": "120px",
                            "height": "20px",
                            "margin-left": "15px",
                        },
                    ),
                    html.Div("- Amp Normalize:"),
                    dcc.RadioItems(
                        options=["on", "off"],
                        value="on",
                        id="crossfilter-xaxis-type",
                        style={"width": "100%"},
                        labelStyle={"marginLeft": "15px"},
                    ),
                    html.Div("- Amp Scale:"),
                    dcc.Input(
                        id="waveform-time-length",
                        type="number",
                        placeholder="amp scale",
                        debounce=True,
                        value=1,
                        style={
                            "width": "120px",
                            "height": "20px",
                            "margin-left": "15px",
                        },
                    ),
                    html.Div("- Yticklabel Num:"),
                    dcc.Input(
                        id="waveform-time-length",
                        type="number",
                        placeholder="second (s)",
                        debounce=True,
                        value=20,
                        style={
                            "width": "120px",
                            "height": "20px",
                            "margin-left": "15px",
                        },
                    ),
                    html.Div("- Bandpass:"),
                    dcc.Input(
                        id="input1",
                        type="number",
                        placeholder="freqmin (hz)",
                        debounce=True,
                        value=20,
                        style={
                            "width": "120px",
                            "height": "20px",
                            "margin-left": "15px",
                        },
                    ),
                    dcc.Input(
                        id="input2",
                        type="number",
                        placeholder="freqmax (hz)",
                        debounce=True,
                        value=20,
                        style={
                            "width": "120px",
                            "height": "20px",
                            "margin-left": "15px",
                        },
                    ),
                    html.Div(id="output"),
                    html.Div("- Velocity:"),
                    dcc.Input(
                        id="waveform-time-length",
                        type="text",
                        placeholder="100,200, (unit)",
                        debounce=True,
                        value="100,200,",
                        style={
                            "width": "120px",
                            "height": "20px",
                            "margin-left": "15px",
                        },
                    ),
                ],
            ),
            html.Br(),
            html.Br(),
        ],
    )

    return div


def beamforming_panel():
    div = html.Div(
        id="control-card",
        style={"width": "100%", "display": "inline-block", "vertical-align": "top"},
        children=[
            html.P("Beamforming"),
            dcc.Input(
                id="noise_source",
                type="text",
                value="0.0",
                style={"width": "120px", "height": "20px", "margin-left": "15px"},
            ),
            html.Br(),
            html.Br(),
        ],
    )
    return div


def ppsd_panel():
    div = html.Div(
        id="control-card",
        style={"width": "100%", "display": "inline-block", "vertical-align": "top"},
        children=[
            html.P("PPSD"),
            dcc.Input(
                id="PPSD",
                type="text",
                value="0.0",
                style={"width": "120px", "height": "20px", "margin-left": "15px"},
            ),
            html.Br(),
            html.Br(),
        ],
    )

    return div


def dvv_panel():
    div = html.Div(
        id="control-card",
        style={"width": "100%", "display": "inline-block", "vertical-align": "top"},
        children=[
            html.P("Dv/v"),
            dcc.Input(
                id="PPSD",
                type="text",
                value="0.0",
                style={"width": "120px", "height": "20px", "margin-left": "15px"},
            ),
            html.Br(),
            html.Br(),
        ],
    )

    return div


# %% right panel
def parameters_show():
    div = html.Div(
        id="parameters-show",
        children=[
            html.Div(
                id="patient_volume_card",
                children=[
                    html.B("Parameters"),
                    html.Hr(),
                    html.Div(row),
                ],
                style={"padding": 10, "flex": 1},
            ),
        ],
        style={"padding": 10, "flex": 1, "display": "block"},
    )

    return div


def map_show():
    div = html.Div(
        id="show-map",
        children=[
            html.Div(
                id="patient_volume_card",
                children=[
                    html.B("Map"),
                    html.Div(
                        daq.ToggleSwitch(
                            id="control-panel-toggle-minute",
                            value=True,
                            label=["waveform", "mat"],
                            color="#85144b",
                            style={
                                "color": "#black",
                                "font-size": "55px",
                                "fontWeight": "bold",
                            },
                        ),
                        style={
                            "position": "absolute",
                            "right": "30px",
                            "top": "15px",
                            "width": "150px",
                        },
                    ),
                    html.Hr(),
                    dcc.Graph(id="map", figure=fig),
                ],
                style={
                    "padding": 10,
                    "flex": 1,
                    "margin": "0px",
                    "position": "relative",
                },
            ),
        ],
        style={"padding": 10, "flex": 1, "display": "block"},
    )

    return div


# %% Create some sample data
rawdata_paras = [
    {"parameter": "channel_number:", "value": str(200)},
    {"parameter": "raw-sampling_rate:", "value": str(100)},
    {"parameter": "detrend:", "value": str(1)},
    {"parameter": "taper:", "value": str("linear")},
    {"parameter": "filter:", "value": str("bandpass")},
    {"parameter": "freqmin:", "value": str(2)},
    {"parameter": "freqmax:", "value": str(2)},
    {"parameter": "re-sampling_rate:", "value": str("2Hz")},
]

rfftdata_paras = [
    {"parameter": "cc_len:", "value": str(70)},
    {"parameter": "cc_step:", "value": str(20)},
    {"parameter": "time_norm:", "value": str("onebit")},
    {"parameter": "clip_std:", "value": str(10)},
    {"parameter": "smooth_N:", "value": str(3)},
    {"parameter": "freq_norm:", "value": str("whiten")},
    {"parameter": "freqmin:", "value": str(1)},
    {"parameter": "freqmax:", "value": str(22)},
    {"parameter": "whiten_npad:", "value": str(50)},
    {"parameter": "smoothspect_N:", "value": str(20)},
    {"parameter": "flag:", "value": str("True")},
    {"parameter": "flag_gap:", "value": str(1)},
    {"parameter": "threads:", "value": str(6)},
]

corrdata_paras = [
    {"parameter": "corr_method:", "value": str("coherency")},
    {"parameter": "maxlag:", "value": str(10)},
    {"parameter": "smoothspect_N:", "value": str(20)},
    {"parameter": "flag:", "value": str("True")},
    {"parameter": "flag_gap:", "value": str(1)},
    {"parameter": "threads:", "value": str(6)},
]

stackdata_paras = [
    {"parameter": "stack_method:", "value": str("linear")},
    {"parameter": "stack_len:", "value": str(20)},
    {"parameter": "stack_step:", "value": str(10)},
    {"parameter": "pick:", "value": str("True")},
    {"parameter": "median_high:", "value": str(3)},
    {"parameter": "median_low:", "value": str(0.5)},
    {"parameter": "flag:", "value": str("True")},
    {"parameter": "flag_gap:", "value": str(1)},
    {"parameter": "threads:", "value": str(6)},
]


# Create a list of Bootstrap cards with scrollable rows
cards = []
for i in range(4):
    if i == 0:
        rows = rawdata_paras
        columns = [
            {"name": "RawData", "id": "parameter"},
            {"name": "Value", "id": "value"},
        ]
    elif i == 1:
        rows = rfftdata_paras
        columns = [
            {"name": "RFFTData", "id": "parameter"},
            {"name": "Value", "id": "value"},
        ]
    elif i == 2:
        rows = corrdata_paras
        columns = [
            {"name": "CorrData", "id": "parameter"},
            {"name": "Value", "id": "value"},
        ]
    elif i == 3:
        rows = stackdata_paras
        columns = [
            {"name": "StackData", "id": "parameter"},
            {"name": "Value", "id": "value"},
        ]

    table = dash_table.DataTable(
        columns=columns,
        data=rows,
        style_as_list_view=True,
        style_cell={"padding": "5px", "textAlign": "left"},
        style_header={
            "backgroundColor": "#85144b",
            "color": "white",
            "fontWeight": "bold",
        },
        style_data_conditional=[
            {"if": {"row_index": "odd"}, "backgroundColor": "rgb(248, 248, 248)"}
        ],
    )
    card_body = dbc.CardBody(table)
    scrollable_row = html.Div(
        card_body, style={"height": "300px", "overflowY": "scroll"}
    )
    cards.append(
        dbc.Card([scrollable_row], style={"marginRight": "1px"})
    )  # width': '250px',

# Combine the cards into a Bootstrap row
row = dbc.Row(
    [
        dbc.Col(cards[0], style={"marginRight": "1px"}),
        dbc.Col(cards[1], style={"marginLeft": "1px"}),
        dbc.Col(cards[2]),
        dbc.Col(cards[3]),
    ],
    style={"marginTop": "20px"},
)


# %%

app.layout = html.Div(
    id="app-container",
    children=[
        # Banner
        html.Div(
            id="banner",
            className="banner",
            children=[
                html.Img(src=app.get_asset_url("plotly_logo.png")),
            ],
        ),
        # Left column
        html.Div(
            id="left-column",
            className="three columns",
            children=[
                description_card(),
                select_plot(),
                map_mode(),
                waveform_panel(),
                spectrogram_panel(),
                stack_panel(),
                moveout_panel(),
                beamforming_panel(),
                ppsd_panel(),
                dvv_panel(),
            ],
        ),
        # Right column
        html.Div(
            id="right-column",
            className="nine columns",
            children=[
                parameters_show(),
                map_show(),
                html.Br(),
                html.Div(
                    id="show-map",
                    children=[
                        html.Div(
                            id="patient_volume_card",
                            children=[
                                html.B("Waveform"),
                                html.Hr(),
                                html.Div(id="output-graph1"),
                            ],
                            style={"padding": 10, "flex": 1},
                        ),
                    ],
                    style={"padding": 10, "flex": 1, "display": "block"},
                ),
                html.Br(),
                html.Div(
                    id="show-waveform",
                    children=[
                        html.Div(
                            id="patient_volume_card",
                            children=[
                                html.B("Waveform"),
                                html.Hr(),
                                html.Div(id="output-graph"),
                                html.Div(
                                    children=[
                                        html.B(html.Label("channels:")),
                                        dcc.RangeSlider(
                                            id="slider-circular",
                                            min=0,
                                            max=9,
                                            step=1,
                                            marks={
                                                i: f"Label {i}" if i == 1 else str(i)
                                                for i in range(1, 10, 2)
                                            },
                                            value=[3, 7],
                                        ),
                                    ],
                                    style={"padding": 1, "flex": 1},
                                ),
                            ],
                            style={"padding": 10, "flex": 1},
                        ),
                    ],
                    style={"padding": 10, "flex": 1, "display": "block"},
                ),
                html.Br(),
                # Patient Volume Heatmap
                html.Div(
                    id="patient_volume_card",
                    children=[
                        html.B("Patient Volume"),
                        html.Hr(),
                        dcc.Graph(id="patient-volume-heatmap"),
                    ],
                ),
                html.Br(),
            ],
        ),
    ],
)


# %%
@app.callback(
    Output("output-graph", "children"),
    Input("slider-circular", "value"),
)
def callback(slider_value):
    fig = generate_figure()

    print(slider_value)
    return encode_image(fig)


@app.callback(
    Output("parameters-show", "style"),
    Input("select-plot", "value"),
)
def callback(value):
    styles = [{"display": "none"}]  # 初始状态所有图像都隐藏
    if "parameters" in value:
        styles[0] = {"display": "block"}

    print(value)
    print(styles[0])

    return styles[0]


@app.callback(
    Output("output-graph1", "children"),
    Input("slider-circular", "value"),
)
def callback(slider_value):
    fig, ax = plt.subplots()
    x = np.linspace(0, 10, 100)
    y = np.sin(x)
    fig, ax = plt.subplots()
    new_y = np.sin(x)
    ax.plot(x, new_y)

    print(slider_value)
    return encode_image(fig)


# Define callback function to update point colors and map zoom/center
@app.callback(
    Output("map", "figure"),
    Input("slider-circular", "value"),
    State("map", "relayoutData"),
)
def update_map(n, relayoutData):
    global mapbox_center, mapbox_zoom

    n = n[1]
    if n > 0 and n <= 100:
        color = ["red"] * 100
        color[n - 1] = "blue"
        text = [
            "Point " + str(i + 1) + ": blue"
            if i == n - 1
            else "Point " + str(i + 1) + ": red"
            for i in range(100)
        ]
        fig.update_traces(marker=dict(color=color), text=text, hovertext=text)

    # Get current map center and zoom from relayoutData
    if relayoutData is not None:
        if "mapbox.center" in relayoutData:
            mapbox_center = go.layout.mapbox.Center(**relayoutData["mapbox.center"])
        if "mapbox.zoom" in relayoutData:
            mapbox_zoom = relayoutData["mapbox.zoom"]

    # Update map center and zoom
    fig.update_layout(
        mapbox_center=mapbox_center,
        mapbox_zoom=mapbox_zoom,
        margin=dict(l=0, r=0, t=0, b=0),
        height=600,
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01),
    )

    return fig


@app.callback(
    Output("output", "children"),
    Input("input2", "value"),
)
def update_output(input2):
    print(input2)
    return None


# %%
if __name__ == "__main__":
    app.run_server(debug=True, port=8051)


# dcc.Checklist(
#    options=[
#        {'label': 'detrend', 'value': 'detrend'},
#        {'label': 'taper', 'value': 'taper'},
#        {'label': 'bandpass', 'value': 'bandpass'},
#    ],
#    value=['detrend','taper','bandpass']
# ),
