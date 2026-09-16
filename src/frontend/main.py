import dash_bootstrap_components as dbc
from dash import Dash
from layouts import main_layout
import callbacks


app = Dash(__name__, url_base_pathname='/frontend/', external_stylesheets=[dbc.themes.BOOTSTRAP])
app.layout = main_layout


@app.server.route('/healthz')
def health_check():
    # Return a simple 200 OK response
    return "OK", 200

@app.server.route('/ready')
def ready_check():
    return "OK", 200


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8050)