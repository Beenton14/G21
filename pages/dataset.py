import dash_bootstrap_components as dbc
from dash import html, dcc
import pandas as pd
import dash
from dash.dependencies import Output, Input

dash.register_page(__name__, path='/dataset', name="Dataset Explorer", order=6)

####################### PAGE LAYOUT #############################
layout = html.Div(children=[
    html.Br(),
    html.H2("Renewable Energy Policy Dataset Explorer", className="fw-bold text-center"),

    # Add a button or dropdown to trigger the data loading
    dbc.Button("Load Dataset", id="load-dataset-btn", color="primary", className="d-block mx-auto"),

    # Adding spinner while data is loading
    dbc.Spinner(  # Wrapping the content in dbc.Spinner
        children=[
            html.Div(id="dataset-table", style={"margin-top": "70px"})  # Change ID to avoid conflict
        ],
        spinner_style={"width": "3rem", "height": "3rem"},  # Custom spinner size
        fullscreen=False  # Spinner is not full screen
    ),
])

####################### CALLBACK #############################
@dash.callback(
    Output("dataset-table", "children"),  # Change to "dataset-table" to avoid circular dependency
    Input("load-dataset-btn", "n_clicks")  # Trigger when button is clicked
)
def update_table(n_clicks):
    if n_clicks is None:
        # Return nothing if the button has not been clicked yet
        return None

    # Load dataset in callback to avoid blocking the main thread
    try:
        df = pd.read_csv("assets/energy_column_data.csv", low_memory=False)
    except Exception as e:
        # Return an error message if there's an issue with the dataset loading
        return dbc.Alert(f"Error loading dataset: {str(e)}", color="danger")

    # Creating Bootstrap Table header and body
    table_header = [html.Thead(html.Tr([html.Th(col) for col in df.columns]))]
    table_body = [html.Tbody([html.Tr([html.Td(df.iloc[i][col]) for col in df.columns])
                              for i in range(min(len(df), 15000))])]  # Limit the number of rows

    # Creating the table layout
    table = dbc.Table(
        table_header + table_body,
        bordered=True,
       
)

    return html.Div(table, style={"margin-top": "20px"})  # Add margin top to the table