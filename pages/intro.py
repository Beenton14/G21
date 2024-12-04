import dash  # Import Dash framework for creating web applications
from dash import html  # Import HTML components from Dash for layout
from dash import dcc  # Import Dash Core Components (for navigation)

# Register the page as the 'Introduction' page for a multi-page Dash app
dash.register_page(__name__, path='/', name="Introduction ", order=0)

####################### PAGE LAYOUT #############################
# Define the layout for the Introduction page
layout = html.Div(children=[  # Create a container div for the whole page


    #  Research Questions
    html.Div(children=[  # Create a div for the Research Questions section
        html.H2("Research Questions"),  # Add a header for the Research Questions section

        # Question 1
        html.B("Question 1"),  # Add bold text for Question 1
        html.P(  # Add the text for Question 1
            "How do public sentiments toward renewable energy policies vary across different countries?"
        ),
        dcc.Link(  # Add a button to navigate to the answers page
            html.Button("Explore Answers", className="btn btn-primary"), href='/stackbar'
        ),  # You can customize the link to lead to the appropriate page
        html.Br(),  # Add a line break for spacing

        # Question 2
        html.B("Question 2 "),  # Add bold text for Question 2
        html.P(  # Add the text for Question 2
            "How have public sentiments towards renewable energy policies evolved from 2018 to 2024, and what energy source may have contributed to changes over the years?"
        ),
        dcc.Link(  # Add a button to navigate to the answers page
            html.Button("Explore Answers", className="btn btn-primary"), href='/Trend_energy'
        ),  # You can customize the link to lead to the appropriate page
        html.Br(),  # Add a line break for spacing

        # Question 3
        html.B("Question 3 "),  # Add bold text for Question 3
        html.P(  # Add the text for Question 3
            "Which renewable energy sources and environmental concerns are prioritized by the public, and how do these influence policy support?"
        ),
        dcc.Link(  # Add a button to navigate to the answers page
            html.Button("Explore Answers", className="btn btn-primary"), href='/network'
        ),  # You can customize the link to lead to the appropriate page
        html.Br(),  # Add a line break for spacing
    ]),



    #Data Source
    html.Div(children=[  # Create a div for the Data Source section
        html.Br(),  # Add a line break for spacing
        html.H2("Data Source"),  # Add a header for the Data Source section
        # List of data sources
        html.P("1. Policy documents from government/public websites"),  # Data source 1
        html.P("2. Public opinion from social media (Reddit and Twitter(X))"),  # Data source 2
        html.Br(),  # Add a line break for spacing
    ])
], className="p-4 m-2", style={"background-color": "#f8f9fa"})  # Add padding and margin for spacing, and set background color
