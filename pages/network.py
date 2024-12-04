import dash  # Import Dash framework for building web applications
import dash_bootstrap_components as dbc  # Import Bootstrap components for styling
from dash import dcc, html, Input, Output  # Import Dash components for layout, inputs, and outputs
import plotly.graph_objects as go  # Import Plotly for visualizations
import networkx as nx  # Import NetworkX for creating network graphs
import pandas as pd  # Import pandas for data manipulation
from nltk.sentiment import SentimentIntensityAnalyzer  # Import sentiment analyzer
import nltk  # Import NLTK for sentiment analysis

# Register the page in Dash app for network visualization
dash.register_page(__name__, path='/network', name="Network", order=4)

# Load DataFrame from the CSV file containing Reddit comments
df = pd.read_csv('assets/reddit_comments.csv')

# Take a random sample of 20% of the records for performance reasons
posts_df = df.sample(frac=0.2, random_state=42)

# Initialize sentiment analyzer (NLTK VADER)
nltk.download('vader_lexicon')
sia = SentimentIntensityAnalyzer()

# Add a new sentiment column to the DataFrame based on comment analysis
def calculate_sentiment(comment):
    if pd.isna(comment):
        return 0  # Treat missing comments as neutral sentiment
    comment = str(comment)
    return sia.polarity_scores(comment)['compound']  # Get compound sentiment score (positive or negative)

# Apply sentiment calculation to each comment
posts_df['sentiment'] = posts_df['comment'].apply(calculate_sentiment)

# Define energy types and sentiment-related words
energy_types = ['solar', 'wind', 'hydropower']
positive_words = ['growth', 'innovation', 'opportunity', 'progress', 'clean', 'advantage']
negative_words = ['crisis', 'loss', 'failure', 'challenge', 'risk', 'pollution']

# Function to calculate frequency of words in the comments
def calculate_frequency(df, words):
    frequency = {word: 0 for word in words}  # Initialize frequency dictionary
    for comment in df['comment'].dropna():  # Iterate over comments, ignoring missing ones
        comment_lower = comment.lower()  # Convert comment to lowercase
        for word in words:
            if word in comment_lower:  # Check if word is in the comment
                frequency[word] += 1  # Increase frequency if the word is found
    return frequency

# Create network graph based on selected energy source and sentiment
def create_network_graph(selected_energy, selected_sentiments):
    G = nx.Graph()  # Initialize an empty network graph

    # Combine positive and negative sentiment words based on user selection
    words = []
    if 'positive' in selected_sentiments:
        words += positive_words
    if 'negative' in selected_sentiments:
        words += negative_words

    # Filter the posts DataFrame to include only comments with the selected energy types
    filtered_posts_df = posts_df[posts_df['comment'].str.contains('|'.join(selected_energy), case=False, na=False)]

    # Calculate frequency of energy types and sentiment words in the comments
    energy_frequency = calculate_frequency(filtered_posts_df, selected_energy)
    sentiment_frequency = calculate_frequency(filtered_posts_df, words)

    # Add energy types as nodes to the graph (only if they appear in the data)
    for energy in selected_energy:
        if energy_frequency[energy] > 0:
            size = max(energy_frequency[energy] * 150, 200)  # Set node size based on frequency
            G.add_node(energy, type='energy', color='skyblue', size=size)  # Add node with size and color

    # Add countries as nodes to the graph
    for country in filtered_posts_df['Country'].unique():
        G.add_node(country, type='Country', color='blue', size=600)  # Fixed size for countries

    # Add sentiment words as nodes to the graph (only if they appear in the data)
    for word in words:
        if sentiment_frequency[word] > 0:
            size = max(sentiment_frequency[word] * 100, 150)  # Set node size based on frequency
            sentiment_color = 'green' if word in positive_words else 'red'  # Green for positive, red for negative
            G.add_node(word, type='sentiment', color=sentiment_color, size=size)  # Add node with size and color

    # Create edges (connections) between nodes based on co-occurrence in the comments
    for idx, row in filtered_posts_df.iterrows():
        comment = str(row['comment']).lower()
        country = row['Country']

        # Create an edge between the energy type and the country
        for energy in selected_energy:
            if energy in comment:
                G.add_edge(energy, country)

                # Create edges between energy type and sentiment words
                for word in words:
                    if word in comment:
                        G.add_edge(energy, word)

    # Define positions for the nodes using NetworkX's spring layout
    pos = nx.spring_layout(G, k=1.2, seed=42)

    # Prepare lists for node and edge coordinates, sizes, colors, and texts for Plotly
    node_x, node_y, node_sizes, node_colors, node_texts = [], [], [], [], []

    for node in G.nodes():
        x, y = pos[node]  # Get node coordinates from the layout
        node_x.append(x)
        node_y.append(y)
        node_sizes.append(G.nodes[node].get('size', 600))  # Default size if not specified
        node_colors.append(G.nodes[node]['color'])
        node_texts.append(f"{node} ({G.nodes[node].get('size', 1)} occurrences)")  # Node text with occurrences

    # Prepare lists for edge coordinates
    edge_x, edge_y = [], []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x += [x0, x1, None]  # Add start and end points for edges
        edge_y += [y0, y1, None]

    # Create Plotly traces for edges (lines) and nodes (markers)
    edge_trace = go.Scatter(
        x=edge_x, y=edge_y, 
        line=dict(width=1.5, color='lightgrey'),  # Edge styling
        hoverinfo='none', 
        mode='lines',  # Display edges as lines
        showlegend=False  # Hide edges from the legend
    )

    node_trace = go.Scatter(
        x=node_x, y=node_y, 
        mode='markers+text',  # Display nodes as markers and show node labels
        marker=dict(
            color=node_colors,
            size=node_sizes,
            sizemode='area',
            line_width=2  # Border around nodes
        ),
        text=[node for node in G.nodes],  # Node labels
        textposition='middle center',  # Center the text on nodes
        hovertext=[f"{node} ({G.nodes[node].get('size', 1)} occurrences)" for node in G.nodes()],  # Hover info
        hoverinfo='text',
        textfont=dict(color='#000000', size=12, family='Arial', weight='bold'),  # Node label styling
        showlegend=False  # Hide nodes from the legend
    )
    
    # Add dummy traces for the legend (for energy, country, positive, and negative words)
    legend_energy = go.Scatter(x=[None], y=[None], mode='markers', marker=dict(size=15, color='skyblue'), name='Energy Source')
    legend_country = go.Scatter(x=[None], y=[None], mode='markers', marker=dict(size=15, color='blue'), name='Country')
    legend_positive = go.Scatter(x=[None], y=[None], mode='markers', marker=dict(size=15, color='green'), name='Positive Word')
    legend_negative = go.Scatter(x=[None], y=[None], mode='markers', marker=dict(size=15, color='red'), name='Negative Word')

    # Create the final Plotly figure layout
    fig = go.Figure(data=[edge_trace, node_trace, legend_energy, legend_country, legend_positive, legend_negative],
                    layout=go.Layout(
                        title=f'Energy Types, Sentiment Words, and Countries Network for {", ".join(selected_energy)}',
                        titlefont_size=20,
                        title_x=0.5,  # Center the title
                        font=dict(family='Arial, sans-serif', size=14, color='#1a3e72'),
                        showlegend=True,  # Show legend
                        hovermode='closest',
                        legend=dict(
                            orientation="v",  # Vertical legend
                            x=1.02,  # Place legend on the right
                            y=1,  # Start legend at the top
                            xanchor='left',
                            yanchor='top'
                        ),
                        margin=dict(b=40, l=40, r=200, t=80),  # Adjust margins for the legend
                        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                        paper_bgcolor='#f8f9fa',
                        plot_bgcolor='#f8f9fa',
                        height=600  # Set height of the graph
                    )
                   )
    return fig

####################### SUMMARY CARDS ###############################
# Create summary cards to display general insights
summary_cards = dbc.Row([
    # Card for average sentiment source
    dbc.Col(dbc.Card(dbc.CardBody([
        html.H5("Average Sentiment Source", className="card-title"),
        html.P("The data is collected from the Reddit and Twitter platforms.", className="card-text"),
        dbc.Button("Average Sentiment Source", href="/average_sentiment", color="primary", className="mt-3", style={"textDecoration": "none"})  # Link to sentiment page
    ]), className="summary-card shadow-sm", style={"text-align": "center"}), width=4),  # Center text and add shadow

    # Card for energy types
    dbc.Col(dbc.Card(dbc.CardBody([
        html.H5("Energy Types", className="card-title"),
        html.P("Focus on Wind, Solar, and Hydropower.", className="card-text")
    ]), className="summary-card", style={"text-align": "center"}), width=4),  # Add shadow and center

    # Card for data source description
    dbc.Col(dbc.Card(dbc.CardBody([
        html.H5("Data Source", className="card-title"),
        html.P("Data is collected from comments on the Reddit and Twitter platforms.", className="card-text")
    ]), className="summary-card", style={"text-align": "center"}), width=4)  # Add shadow and center
], className="mb-4")  # Add margin at the bottom


####################### PAGE LAYOUT #############################
# Layout for the network visualization page
layout = dbc.Container([
    # Display the summary cards at the top
    summary_cards,

    # Title for the page
    dbc.Row([
        dbc.Col(html.H1("Energy Types, Sentiment Co-occurrence, and Countries Network", className="text-center text-primary mb-4", style={"color": "#007bff"}), width=12)
    ]),

    # Dropdowns for selecting energy type and sentiment type
    dbc.Row([
        # Dropdown for selecting energy source
        dbc.Col([
            dbc.Card(
                dbc.CardBody([               
                    html.Label('Select Energy Source:', className='font-weight-bold'),
                    dcc.Dropdown(
                        id='energy-dropdown',
                        options=[{'label': 'All', 'value': 'All'}] + [{'label': energy.capitalize(), 'value': energy} for energy in energy_types],
                        value='All',  # Default to 'All'
                        multi=False,  # Single selection
                        className='mb-3'
                    )
                ])
            )
        ], width=6),

        # Dropdown for selecting sentiment type
        dbc.Col([
            dbc.Card(
                dbc.CardBody([                  
                    html.Label('Select Sentiment Type:', className='font-weight-bold'),
                    dcc.Dropdown(
                        id='sentiment-dropdown',
                        options=[{'label': 'All', 'value': 'All'}, {'label': 'Positive', 'value': 'positive'}, {'label': 'Negative', 'value': 'negative'}],
                        value='All',  # Default to 'All'
                        multi=False,  # Single selection
                        className='mb-3'
                    )
                ])
            )
        ], width=6)
    ]),

    # Display the network graph
    dbc.Row([
        dbc.Col([
            dcc.Graph(id='network-graph')  # Graph component to show the network
        ], width=20)
    ]),

    # Add extra spacing at the bottom of the page
    html.Div(children=[
        html.Br(),
        html.Br(),
        html.Br(),
        html.Br()   
    ])
], fluid=True)

####################### CALLBACK ##############################
# Callback to update the graph based on dropdown values
@dash.callback(
    Output('network-graph', 'figure'),
    [Input('energy-dropdown', 'value'),
     Input('sentiment-dropdown', 'value')]
)
def update_graph(selected_energy, selected_sentiment):
    # Replace 'All' with all energy types or sentiment types
    if selected_energy == 'All':
        selected_energy = energy_types
    else:
        selected_energy = [selected_energy]
    
    if selected_sentiment == 'All':
        selected_sentiment = ['positive', 'negative']
    else:
        selected_sentiment = [selected_sentiment]
    
    # Return the updated network graph based on selected options
    return create_network_graph(selected_energy, selected_sentiment)
