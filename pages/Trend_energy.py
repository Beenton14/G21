import plotly.graph_objs as go  # Import Plotly for creating interactive visualizations
from dash import dcc, html  # Import Dash components for layout and interactivity
from dash.dependencies import Input, Output  # Import Input and Output for callbacks
import pandas as pd  # Import pandas for data manipulation
import dash  # Import Dash framework for building the web app
import dash_bootstrap_components as dbc  # Import Bootstrap components for better styling

# Register the page in a multi-page Dash app
dash.register_page(__name__, path='/Trend_energy', name="Trends", order=2)

# Define the layout for this page
layout = dbc.Container([
    # Title and description row
    dbc.Row([
        dbc.Col(html.H1("Sentiment Trends", className="text-center my-4", 
                        style={'font-size': '36px', 'font-weight': 'bold', 'color': '#1a3e72'}), width=12),
    ]),
    dbc.Row([
        dbc.Col(html.P(
            "Use the filters below to explore sentiment trends across countries and energy sources from 2018 to 2024.",
            className="text-center mb-4", style={'font-size': '18px', 'color': '#6c757d'}
        ), width=12),
    ]),

    # Filter section with two dropdowns for country and energy source
    dbc.Row([
        dbc.Col([
            dbc.Card(
                dbc.CardBody([
                    # Dropdown to filter by country
                    dbc.Label("Filter by Country", style={'font-size': '16px', 'font-weight': 'bold'}),
                    dcc.Dropdown(
                        id='country-filter',
                        options=[],  # Will be populated via callback
                        value=None,  # Default value will be set via callback
                        clearable=False,
                        className="mb-3",
                        style={'border-radius': '8px', 'background-color': '#f7f7f7'}
                    ),
                    # Dropdown to filter by energy source
                    dbc.Label("Filter by Energy Source", style={'font-size': '16px', 'font-weight': 'bold'}),
                    dcc.Dropdown(
                        id='energy-filter',
                        options=[],  # Will be populated via callback
                        value=None,  # Default value will be set via callback
                        clearable=False,
                        className="mb-3",
                        style={'border-radius': '8px', 'background-color': '#f7f7f7'}
                    )
                ])
            )
        ], width=6),
        # Year range filter using a RangeSlider
        dbc.Col([
            dbc.Card(
                dbc.CardBody([
                    html.H5("Select Year Range", className="card-title", style={'font-size': '20px'}),
                    dcc.RangeSlider(
                        id='year-range-slider',
                        min=2018,  # Minimum year for the slider
                        max=2024,  # Maximum year for the slider
                        step=1,  # Slider steps by year
                        marks={year: str(year) for year in range(2018, 2025)},  # Display marks for each year
                        value=[2018, 2024],  # Default range from 2018 to 2024
                        className="mb-3",
                        tooltip={"placement": "bottom", "always_visible": True},
                        allowCross=False  # Disable crossing of year range handles
                    )
                ])
            )
        ], width=6),
    ], className="mb-4"),

    # Loading spinner that appears when the graph is being updated
    dcc.Loading(
        id="loading-graph",
        type="circle",
        children=[
            # Line graph to display sentiment trends
            dbc.Row([
                dbc.Col([
                    dcc.Graph(id='line-graph', className="mb-5", config={"displayModeBar": False})  # Disable toolbar
                ], width=12),
            ]),
        ]
    ),

    # Footer with the data source information
    dbc.Row([ 
        dbc.Col(html.P("Data Source: Renewable Energy Public Sentiment (2018-2024)", 
                       className="text-muted text-center mb-4", 
                       style={'font-size': '14px'}), width=12)
    ]),
], fluid=True)  # fluid=True ensures the layout is responsive and uses the full page width

# Callback function to update the dropdown filters and the line graph
@dash.callback(
    [Output('country-filter', 'options'),  # Dropdown options for country
     Output('country-filter', 'value'),  # Default value for country
     Output('energy-filter', 'options'),  # Dropdown options for energy source
     Output('energy-filter', 'value'),  # Default value for energy source
     Output('line-graph', 'figure')],  # Line graph figure
    [Input('country-filter', 'value'),  # Input from selected country
     Input('energy-filter', 'value'),  # Input from selected energy source
     Input('year-range-slider', 'value')]  # Input from selected year range
)
def update_graph(selected_country, selected_energy, selected_years):
    # Load the data inside the callback function
    file_path = 'assets/trend_data.csv'  # Path to the CSV file containing sentiment data
    try:
        df = pd.read_csv(file_path)
    except Exception as e:
        return [{'label': 'Error', 'value': 'Error'}], 'Error', [], 'Error', go.Figure()

    # Convert 'comment_date' to datetime and extract year from it
    df['comment_date'] = pd.to_datetime(df['comment_date'], format='%d/%m/%Y', errors='coerce')
    df['year'] = df['comment_date'].dt.year

    # Drop rows with missing year data and convert 'year' to integers
    df = df.dropna(subset=['year'])
    df['year'] = df['year'].astype(int)

    # Group the data by year, country, energy source, and sentiment
    sentiment_trends = df.groupby(['year', 'country', 'energy_source', 'sentiment']).size().unstack(fill_value=0).reset_index()

    # Create country options for the dropdown
    country_options = [{'label': country, 'value': country} for country in sentiment_trends['country'].unique()]
    
    # Create energy source options for the dropdown
    energy_options = [{'label': energy, 'value': energy} for energy in sentiment_trends['energy_source'].unique()]

    # Set default values if none are selected
    if not selected_country:
        selected_country = country_options[0]['value']  # Default to first available country

    if not selected_energy:
        selected_energy = energy_options[0]['value']  # Default to first available energy source

    # Filter the data based on selected country, energy source, and year range
    filtered_data = sentiment_trends[
        (sentiment_trends['country'] == selected_country) &
        (sentiment_trends['energy_source'] == selected_energy) &
        (sentiment_trends['year'] >= selected_years[0]) &
        (sentiment_trends['year'] <= selected_years[1])
    ]

    # Create line traces for positive and negative sentiments, using smoothing for better visual
    fig = go.Figure()
    if not filtered_data.empty:
        # Trace for positive sentiment
        fig.add_trace(go.Scatter(
            x=filtered_data['year'], y=filtered_data['positive'], mode='lines+markers',
            name='Positive', 
            line=dict(color='#28a745', width=4, shape='spline', smoothing=1.3),  # Green for positive sentiment
            marker=dict(size=8),
            hoverinfo='x+y+name', hovertemplate='<b>Year:</b> %{x}<br><b>Positive:</b> %{y}'
        ))
        # Trace for negative sentiment
        fig.add_trace(go.Scatter(
            x=filtered_data['year'], y=filtered_data['negative'], mode='lines+markers',
            name='Negative', 
            line=dict(color='#dc3545', width=4, shape='spline', smoothing=1.3),  # Red for negative sentiment
            marker=dict(size=8),
            hoverinfo='x+y+name', hovertemplate='<b>Year:</b> %{x}<br><b>Negative:</b> %{y}'
        ))
    else:
        fig.update_layout(title="No data for selected filters")

    # Update layout of the figure
    fig.update_layout(
        title={  # Set the title in the center
        'text': f"Sentiment Trends in {selected_country} for {selected_energy}",
        'x': 0.5,  # Center the title horizontally
        'xanchor': 'center',  # Anchor title to the center
        'yanchor': 'top',  # Anchor title to the top
    },
        title_font=dict(size=26, family='Arial', color='#1a3e72'),
        xaxis_title="Year",
        xaxis_title_font=dict(size=18, family='Arial', color='#1a3e72'),
        yaxis_title="Sentiment Count",
        yaxis_title_font=dict(size=18, family='Arial', color='#1a3e72'),
        xaxis=dict(
            tickmode='linear',
            dtick=1,    # Ensure ticks appear every year
            showgrid=True
        ),
        yaxis=dict(
            showgrid=True,  # Show gridlines for readability
            tickfont=dict(size=14, color='#1a3e72'),  # Font size for y-axis ticks
        ),
        template="plotly_white",
        hovermode="x unified",  # Hovermode for displaying all data at the x-axis point
        showlegend=True,
        legend=dict(title="Sentiment", orientation="h", y=1.1, x=1, xanchor='right', font=dict(size=14)),
        hoverlabel=dict(bgcolor="white", font_size=14, font_family="Arial"),
        margin=dict(l=20, r=20, t=60, b=40)  # Margins around the figure
    )

    # Return updated dropdown options, selected values, and the figure
    return country_options, selected_country, energy_options, selected_energy, fig
