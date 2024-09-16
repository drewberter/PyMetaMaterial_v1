import dash
import dash_bootstrap_components as dbc
from dash import dcc, html
from dash.dependencies import Input, Output, State
from modules.simulation_module import simulate_metamaterial
from modules.design_module import design_metamaterial
from modules.visualization_module import plot_attenuation

# Initialize Dash app with Bootstrap stylesheet
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Define layout
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H2("Acoustic Metamaterial Design", className="text-center mt-4"),
            dcc.Dropdown(
                id='material-dropdown',
                options=[
                    {'label': 'Silicone Rubber', 'value': 'Silicone Rubber'},
                    {'label': 'Polyurethane', 'value': 'Polyurethane'}
                ],
                value='Silicone Rubber',
                className="mb-3"
            ),
            dcc.Slider(id='freq-min-slider', min=100, max=500, step=50, value=200),
            dcc.Slider(id='freq-max-slider', min=500, max=2000, step=50, value=1000),
            dbc.Button("Run Design and Simulation", id="run-simulation", className="btn btn-primary mt-3"),
        ], width=4),
        dbc.Col([
            dcc.Loading(id="loading", children=[
                dcc.Graph(id='attenuation-graph')  # Only assign ID here
            ], type="circle"),
        ], width=8),
    ])
])

# Callback to update graph
@app.callback(
    [Output('attenuation-graph', 'figure')],
    [Input('run-simulation', 'n_clicks')],
    [State('freq-min-slider', 'value'), State('freq-max-slider', 'value'), State('material-dropdown', 'value')]
)
def update_graph(n_clicks, freq_min, freq_max, material):
    if n_clicks is None:
        return dash.no_update
    
    # Design metamaterial dimensions
    dimensions = design_metamaterial(freq_min, freq_max, material)

    # Simulate the metamaterial based on the designed dimensions
    frequencies, attenuation = simulate_metamaterial(dimensions)

    # Plot the attenuation results
    fig = plot_attenuation(frequencies, attenuation)

    return [fig]

if __name__ == "__main__":
    app.run_server(host="0.0.0.0", port=8050, debug=True)
