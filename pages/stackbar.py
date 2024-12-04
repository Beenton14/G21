import dash  # Import Dash for building the web application
from dash import dcc, html, callback, Input, Output  # Import Dash components for interactivity and callbacks
import plotly.express as px  # Import Plotly Express for data visualizations
import dash_bootstrap_components as dbc  # Import Bootstrap components for styling
import pandas as pd  # Import pandas for data manipulation

# Register the page in a multi-page Dash app
dash.register_page(__name__, path='/stackbar', name="Overview", order=1)

# Load the dataset from the CSV file
df = pd.read_csv('assets/energy_column_data.csv')

####################### STACKED BAR CHART ###############################
# Function to create a stacked bar chart showing sentiment analysis for a given energy source
def create_sentiment_chart(energy_source):
    # Filter the dataframe based on the selected energy source
    filtered_df = df[df['energy_source'] == energy_source]

    # Group the data by country and sentiment, and calculate the count
    sentiment_count = filtered_df.groupby(['country', 'sentiment']).size().reset_index(name='count')

    # Normalize the count to percentage for each country
    sentiment_count['Percentage'] = sentiment_count.groupby('country')['count'].transform(lambda x: (x / x.sum()) * 100)

    # Create the stacked bar chart using Plotly Express
    fig = px.bar(
        sentiment_count,
        x='country',  # X-axis is the country
        y='Percentage',  # Y-axis is the percentage of sentiment
        color='sentiment',  # Color based on sentiment (positive, neutral, negative)
        height=450,  # Height of the chart
        title=f'Sentiment Analysis on {energy_source} Energy by Country',  # Title of the chart
        labels={'Percentage': 'Percentage of Sentiment', 'country': 'Country'},  # Axis labels
        color_discrete_map={'positive': '#8FBC8F', 'neutral': 'grey', 'negative': 'salmon'},  # Colors for each sentiment type
        text='Percentage',  # Display percentage text on bars
    )

    # Format the text and tooltips in the bar chart
    fig.update_traces(texttemplate='%{text:.1f}', textposition='auto')  # Format percentage text on bars
    fig.update_traces(hovertemplate='<b>%{x}</b><br>Percentage: %{y:.2f}%<br>')  # Tooltip format

    # Update layout to make the bar chart more readable
    fig.update_layout(
        barmode='stack',  # Stack the bars for different sentiments
        xaxis={'categoryorder': 'total descending'},  # Sort countries by total sentiment count
        yaxis_title='Percentage of Sentiment',  # Y-axis title
        xaxis_title='Country',  # X-axis title
        margin={"t": 50, "b": 50, "l": 50, "r": 50},  # Margins around the chart
        font=dict(size=15),  # Font size for the chart
        title=dict(x=0.5, xanchor='center', yanchor='middle', font=dict(size=17)),  # Title formatting
        legend_title_text='Sentiment',  # Legend title
        legend=dict(orientation='v', yanchor='top', y=1, xanchor='left', x=1.05)  # Legend position
    )
    
    # Show gridlines and set the background color
    fig.update_yaxes(showgrid=True, gridcolor='lightgrey')
    fig.update_layout(paper_bgcolor='#f8f9fa', plot_bgcolor='#f8f9fa')  # Light background colors
    
    return fig

####################### PIE CHART ###############################
# Function to create a pie chart showing the distribution of a specific sentiment by country for a given energy source
def create_country_sentiment_pie_chart(energy_source, sentiment_type):
    # Filter the dataframe by both energy source and sentiment type
    filtered_df = df[(df['energy_source'] == energy_source) & (df['sentiment'] == sentiment_type)]

    # Group the data by country and calculate the count of each sentiment
    country_summary = filtered_df.groupby('country').size().reset_index(name='count')

    # Normalize the count to percentage for the pie chart
    country_summary['Percentage'] = country_summary['count'] / country_summary['count'].sum() * 100

    # Create the pie chart using Plotly Express
    fig = px.pie(
        country_summary,
        values='Percentage',  # Values for the pie chart
        names='country',  # Categories (countries) for the pie chart
        title=f'{sentiment_type.capitalize()} Sentiment Distribution for {energy_source} Energy',  # Title
        color='country',  # Color by country
        color_discrete_map={'Australia': '#1f77b4', 'UK': '#ff7f0e', 'France': '#2ca02c'}  # Custom colors for countries
    )
    
    # Format the tooltips in the pie chart
    fig.update_traces(hovertemplate='<b>%{label}</b><br>Percentage: %{value:.2f}%<br>')

    # Update layout for the pie chart
    fig.update_layout(
        font=dict(size=15),  # Font size
        title=dict(x=0.5, xanchor='center', yanchor='middle', font=dict(size=17)),  # Title formatting
        margin={"t": 50, "b": 50, "l": 50, "r": 50},  # Margins around the chart
        legend_title_text='Country',  # Legend title
        paper_bgcolor='#f8f9fa'  # Light background color
    )
    
    return fig

####################### WIDGETS ################################
# Dropdown to select energy type
dd = dcc.Dropdown(
    id="energy_type_dropdown",
    options=[{"label": et, "value": et} for et in df['energy_source'].unique()],  # Options are unique energy sources
    value="Wind",  # Default value is Wind energy
    clearable=False,  # User cannot clear the selection
    style={'width': '100%'}  # Full width dropdown
)

# Checklist to select sentiment types (positive, neutral, negative)
sentiment_checkbox = dcc.Checklist(
    id="sentiment_type_checklist",
    options=[
        {'label': 'Positive', 'value': 'positive'},
        {'label': 'Neutral', 'value': 'neutral'},
        {'label': 'Negative', 'value': 'negative'}
    ],
    value=['positive'],  # Default selection is positive sentiment
    inline=True,  # Display checklist inline
    style={'font-size': '20px'},  # Font size for checklist
    className="dash-checkbox-group"
)

####################### SUMMARY CARDS ###############################
# Summary cards to display key information on the page
summary_cards = dbc.Row([
    # First card: Data source information
    dbc.Col(dbc.Card(dbc.CardBody([
        html.H5("Data Source", className="card-title"),  # Title
        html.P("The data is collected from Reddit and Twitter platforms.", className="card-text"),  # Description
        dbc.Button("Explore Dataset", href="/dataset", color="primary", className="mt-3", style={"textDecoration": "none"})  # Link to explore dataset
    ]), className="summary-card shadow-sm", style={"text-align": "center"}), width=4),
    
], className="mb-4 justify-content-center")

####################### PAGE LAYOUT #############################
# Main layout for the page
layout = dbc.Container([
    # Page title
    dbc.Row([
        dbc.Col(html.H2("Sentiment Analysis by Energy Type and Country", className="text-center mb-4"), width=12)
    ]),
    # Row with dropdown for energy type and checklist for sentiment type
    dbc.Row([
        dbc.Col(html.Label("Energy Type:", style={'font-size': '20px', 'padding-right': '0px'}), width='auto', style={'display': 'flex', 'align-items': 'center'}),  # Label for energy type
        dbc.Col(dd, width=4, style={'margin-top': '30px', 'margin-left': '0px'}),  # Dropdown for energy type
        dbc.Col(html.Label("Sentiment Type:", style={'font-size': '20px', 'padding-left': '90px'}), width='auto', style={'display': 'flex', 'align-items': 'center'}),  # Label for sentiment type
        dbc.Col(sentiment_checkbox, width=2)  # Checklist for sentiment type
    ], className='mb-4 justify-content-center'),
    
    # Row to display the stacked bar chart and pie chart
    dbc.Row([
        dbc.Col(dcc.Graph(id="sentiment_chart", config={'responsive': True}, style={'width': '100%', 'height': 'auto'}), width=5, className="d-flex justify-content-center"),  # Stacked bar chart
        dbc.Col(dcc.Graph(id="sentiment_pie_chart", config={'responsive': True}, style={'width': '100%', 'height': 'auto'}), width=5, className="d-flex justify-content-center")  # Pie chart
    ], className='justify-content-center'),

    # Summary cards to display additional information
    dbc.Row([
        dbc.Col(summary_cards, width=12, style={'margin-top': '30px'})  # Added margin-top to summary cards
    ])
], fluid=True, className="p-4 bg-light")# Fluid layout for responsiveness

####################### CALLBACKS ##############################
# Callback function to update the charts when user selects new energy type or sentiment types
@callback(
    [Output("sentiment_type_checklist", "value"), Output("sentiment_chart", "figure"), Output("sentiment_pie_chart", "figure")],
    [Input("energy_type_dropdown", "value"), Input("sentiment_type_checklist", "value")]
)
def update_charts(energy_type, sentiment_types):
    # If no sentiment types are selected, default to 'positive'
    if not sentiment_types:
        sentiment_types = ['positive']
    # Limit the selection to one sentiment type
    if len(sentiment_types) > 1:
        sentiment_types = [sentiment_types[-1]]
    
    # Update the stacked bar chart and pie chart based on the selected energy type and sentiment type
    return sentiment_types, create_sentiment_chart(energy_type), create_country_sentiment_pie_chart(energy_type, sentiment_types[0])
