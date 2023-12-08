import os, sys
from dash import Dash, html, dcc, callback, Output, Input

sys.path.append("/Users/yinfu/ohmyshake/shakeflow")
from shakeflow import file_monitor

"""
    When event_handler is changed from the watchdog thread, the callback will be triggered automatically.

"""

app = Dash(__name__)


path = "/Users/yinfu/ohmyshake/shakeflow/examples/raspberry_shake_ambient_noise"

# thread-1: file monitor
observer, event_handler = file_monitor(path, mode="from_origin", suffix=".py")
observer.start()


app.layout = html.Div(
    [
        dcc.Interval(id="interval-component", interval=1 * 1000, n_intervals=0),
        html.Div(id="file-change-output"),
    ]
)


@callback(
    Output("file-change-output", "children"), Input("interval-component", "n_intervals")
)
def update_output(n):
    print(n, event_handler.files[-1])
    return f"current time: {n}"


if __name__ == "__main__":
    app.run_server(debug=True)
