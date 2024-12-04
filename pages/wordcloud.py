import dash  # Import Dash framework for creating the web app
from dash import dcc, html, Input, Output  # Import Dash components for layout and callbacks
import pandas as pd  # Import pandas for data manipulation
from wordcloud import WordCloud  # Import WordCloud for generating word clouds
import plotly.express as px  # Import Plotly Express for easy data visualization
import io  # Import io to handle in-memory image operations
import base64  # Import base64 to encode image to base64 format for display in the app
import dash_bootstrap_components as dbc  # Import Bootstrap components for responsive design

# Register the page in the multi-page app, with a specific path and name
dash.register_page(__name__, path='/wordcloud', name="WordInsight", order=3)

# Load the word frequencies from CSV files (data from Twitter and Reddit)
tweets_df = pd.read_csv('assets/tweets_word_frequency.csv')  # Load Twitter word frequency data
reddit_df = pd.read_csv('assets/reddit_word_frequency.csv')  # Load Reddit word frequency data

# Function to create a word cloud image from word frequencies
def create_wordcloud(frequencies):
    # Generate the word cloud image with a white background
    wordcloud = WordCloud(width=1200, height=600, background_color='white').generate_from_frequencies(frequencies)
    # Convert the image to binary format for in-memory operations
    img = io.BytesIO()
    wordcloud.to_image().save(img, format='PNG')  # Save the word cloud as a PNG image
    img.seek(0)  # Move to the start of the image buffer
    # Return the image encoded in base64 to display in the web app
    return base64.b64encode(img.getvalue()).decode()

# Layout for the page (using Dash Bootstrap Components for styling)
def layout():
    return dbc.Container([  # Use dbc.Container for a responsive layout
        dbc.Row([  # First row for the page title
            dbc.Col(html.H3("Most Frequently Used Words in Renewable Energy Policy Discussions", 
                            style={'textAlign': 'center', 'padding': '20px'}), width=12)  # Center the title
        ]),
        
        dbc.Row([  # Second row for the dropdown menu
            dbc.Col(
                dcc.Dropdown(  # Dropdown for selecting between Reddit and Twitter data
                    id='source-selector',
                    options=[  # Dropdown options
                        {'label': 'Reddit', 'value': 'reddit'},
                        {'label': 'Twitter', 'value': 'twitter'}
                    ],
                    value='reddit',  # Set Reddit as the default option
                    style={'margin': '20px', 'width': '100%'}  # Full width dropdown with margin
                ),
                width=6,  # Set dropdown width to half of the row
                className="mx-auto"  # Center the dropdown
            )
        ]),

        dbc.Row([  # Third row for the bar chart display
            dbc.Col(
                dcc.Graph(id='bar-chart'),  # Bar chart to display top 10 word frequencies
                width=12  # Set column width to full width
            )
        ]),

        dbc.Row([  # Fourth row for displaying the word cloud
            dbc.Col(
                html.Div([  # Div container for the word cloud image
                    html.Img(id='wordcloud-img', style={'width': '80%', 'height': 'auto', 'marginTop': '0px'})
                ], style={'display': 'flex', 'justifyContent': 'center', 'alignItems': 'center', 
                          'height': '700px', 'backgroundColor':'#f8f9fa'}),  # Center the image and add styling
                width=12  # Set column width to full width
            )
        ])
    ], fluid=True)  # Fluid container to ensure responsiveness

# Callback to update both the word cloud and the bar chart based on the selected data source
@dash.get_app().callback(
    [Output('wordcloud-img', 'src'),  # Output for the word cloud image
     Output('bar-chart', 'figure')],  # Output for the bar chart figure
    [Input('source-selector', 'value')]  # Input from the dropdown selector (source-selector)
)
def update_visualizations(source):
    # Select the appropriate data based on the user’s input (Reddit or Twitter)
    if source == 'reddit':
        df = reddit_df  # Use Reddit data
    else:
        df = tweets_df  # Use Twitter data

    # Generate the word cloud using word frequencies
    word_freq_dict = dict(zip(df['word'], df['frequency']))  # Create a dictionary from the DataFrame
    wordcloud_src = f"data:image/png;base64,{create_wordcloud(word_freq_dict)}"  # Generate base64 encoded image

    # Create the bar chart for the top 10 most frequent words
    top_10_df = df.nlargest(10, 'frequency')  # Select top 10 words by frequency
    bar_chart = px.bar(top_10_df, x='frequency', y='word', orientation='h', title="Top 10 Words Frequency")  # Create horizontal bar chart
    # Customize the bar chart layout
    bar_chart.update_layout(
        plot_bgcolor='rgba(255, 0, 0, 0)',  # Set plot area background (transparent)
        paper_bgcolor='#f8f9fa',  # Set paper area background
        title_font=dict(size=24),  # Adjust title font size
        font=dict(size=16)  # Adjust general font size
    )
    
    # Return the updated word cloud image source and bar chart figure
    return wordcloud_src, bar_chart
