import pandas as pd  # Import pandas for data manipulation
import dash  # Import Dash for creating the web application
from dash import dcc, html  # Import Dash components for layout
from dash.dependencies import Input, Output  # Import Input and Output for creating callbacks
import plotly.express as px  # Import Plotly Express for data visualization
import dash_bootstrap_components as dbc  # Import Bootstrap components for styling

# Registering the page for a multi-page Dash app with specific path and name
dash.register_page(__name__, path='/average_sentiment', name="Average Sentiment", order=5)

# Load the dataset containing Reddit comments with policy and sentiment analysis
df = pd.read_csv("assets/reddit_comments.csv")

####################### PAGE LAYOUT #############################
# Define the layout for the page using Dash Bootstrap Components for styling
layout = dbc.Container([  # Create a responsive container for the page
    # Header row with the title
    dbc.Row([
        dbc.Col(html.H1("Average Sentiment per Policy by Country", className="text-center text-primary mb-4"), width=12)
    ]),
    
    # Row for the country selection dropdown
    dbc.Row([ 
        dbc.Col(dcc.Dropdown(
            id='country-dropdown',  # Dropdown ID for use in the callback
            options=[{'label': 'All', 'value': 'All'}] + [{'label': country, 'value': country} for country in df['Country'].unique()],  # Options: 'All' or individual countries
            value='All',  # Default selected value is 'All'
            clearable=False,  # Do not allow the user to clear the selection
            style={'width': '50%'}  # Set the width of the dropdown
        ), width=6)  # Set the dropdown width to 6 columns (half width)
    ], justify="center", style={'margin-top': '20px'}),  # Center the dropdown and add margin for spacing
    
    # Row to display the bar chart for sentiment analysis
    dbc.Row([ 
        dbc.Col(dcc.Graph(id='policy-sentiment-bar-chart'), width=12)  # Create a column for the bar chart graph
    ])
], style={'backgroundColor': '#f8f9fa'})  # Set the background color for the page

####################### CALLBACKS ################################
# Callback function to update the bar chart based on the selected country
@dash.callback(
    Output('policy-sentiment-bar-chart', 'figure'),  # The output is the figure for the bar chart
    [Input('country-dropdown', 'value')]  # The input is the value from the country dropdown
)
def update_bar_chart(selected_country):
    # If 'All' is selected, use the entire dataset without filtering
    if selected_country == 'All':
        filtered_data = df
    else:
        # Filter the dataset based on the selected country
        filtered_data = df[df['Country'] == selected_country]
    
    # Group the data by policy and calculate the average sentiment (compound score)
    policy_avg_sentiment = filtered_data.groupby('policy')['compound'].mean().reset_index()
    
    # Convert the policy names to uppercase for better readability
    policy_avg_sentiment['policy'] = policy_avg_sentiment['policy'].str.upper()
    
    # Sort the data by the compound sentiment score in descending order
    policy_avg_sentiment = policy_avg_sentiment.sort_values(by='compound', ascending=False)
    
    # Create a horizontal bar chart using Plotly Express
    fig = px.bar(
        policy_avg_sentiment,  # Data to visualize
        x='compound',  # X-axis is the average sentiment score
        y='policy',  # Y-axis is the policy name
        orientation='h',  # Create a horizontal bar chart
        labels={'compound': 'Average Sentiment (Compound Score)', 'policy': 'Policy'},  # Axis labels
        title=f'Average Sentiment per Policy in {selected_country}' if selected_country != 'All' else 'Average Sentiment per Policy for All Countries',  # Title based on selection
        template='plotly_white'  # Use the white theme for the chart
    )
    
    # Invert the y-axis to display the highest sentiment at the top
    fig.update_layout(
        yaxis=dict(autorange="reversed"),
        height=600,  # Set the height of the figure
        paper_bgcolor='#f8f9fa',  # Set the background color of the figure
        title={  # Configure the title
            'text': f'Average Sentiment per Policy in {selected_country}' if selected_country != 'All' else 'Average Sentiment per Policy for All Countries',
            'y': 0.95,  # Set the vertical position of the title
            'x': 0.5,  # Center the title horizontally
            'xanchor': 'center',  # Set the horizontal anchor to the center
            'yanchor': 'top',  # Set the vertical anchor to the top
            'font': {'size': 22, 'color': '#2a3f5f'}  # Set the font size and color for the title
        },
        xaxis_title=dict(
            text='Average Sentiment (Compound Score)',  # Set the label for the x-axis
            font={'size': 18, 'color': '#4b4b4b'}  # Set font size and color for the x-axis label
        ),
        yaxis_title=dict(
            text='Policy',  # Set the label for the y-axis
            font={'size': 18, 'color': '#4b4b4b'}  # Set font size and color for the y-axis label
        ),
        font=dict(
            family='Arial, sans-serif',  # Set the font family
            size=14,  # Set the general font size
            color='#2a3f5f'  # Set the general font color
        ),
        hoverlabel=dict(
            font_size=14,  # Set the font size for hover labels
            font_family="Arial"  # Set the font family for hover labels
        ),
        margin=dict(l=100, r=20, t=50, b=50)  # Set margins for the figure layout
    )
    
    # Customize the hover info to show sentiment with 3 decimal places
    fig.update_traces(
        hovertemplate='<b>%{y}</b><br>Average Sentiment: %{x:.3f}<extra></extra>',  # Set hover text format
        marker_color='#3498db'  # Set the color of the bars
    )
    
    # Return the updated figure
    return fig
