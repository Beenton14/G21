from dash import Dash, html, dcc
import dash
import dash_bootstrap_components as dbc  # Import Bootstrap components for Dash

# List of external CSS stylesheets to be used in the app, including Bootstrap for layout and custom CSS for additional styling
external_css = [
    dbc.themes.BOOTSTRAP,  # Bootstrap theme from Dash Bootstrap Components
    "https://cdn.jsdelivr.net/npm/bootstrap@5.3.1/dist/css/bootstrap.min.css",
    "assets/custom.css"  # 'custom.css' should be located in the 'assets' folder for custom styles
]

# Initialize the Dash app with the specified external stylesheets and enable multi-page functionality using 'pages_folder' and 'use_pages'
app = Dash(__name__, pages_folder='pages', use_pages=True, external_stylesheets=external_css)

# Create an image element for the brand logo (GrrenPulse), specifying the source, width, and margin classes for styling
img_tag = html.Img(src="assets/greenpulse.png", width=25, className="m-1")

# Create a navigation brand link using the image and text, setting the hyperlink to the homepage ('#')
brand_link = dcc.Link([img_tag, "  G21 "], href="#", className="navbar-brand d-flex align-items-center", style={"font-size": "1.2rem"})

# Generate a list of navigation links for each page in the Dash app using the page registry, which maps page names to their relative paths
pages_links = [dcc.Link(page['name'], href=page["relative_path"], className="nav-link") \
               for page in dash.page_registry.values() if page['name'] not in ['Dataset Explorer','Average Sentiment']]

# Layout of the app
app.layout = html.Div([
    # Navbar 
    html.Nav(children=[
        html.Div([  # Container for navigation links
            # Group brand link and page links into a navigation div for Bootstrap styling
            html.Div([brand_link, ] + pages_links, className="navbar-nav")
        ], className="container-fluid"),
    ], className="navbar navbar-expand-lg bg-dark", **{"data-bs-theme": "dark"}),  # Bootstrap navbar with dark theme

    
    # Main page 
    html.Div([
        html.Br(),  # Add a line break for spacing
        # Header text for the main page
        html.P('Renewable Energy Policy and Community Engagement Insights Platform', className="text-dark text-center fw-bold fs-1"),
        # Container for rendering the content of the current page dynamically
        dash.page_container
    ], className="page-container")  # Center the main content with responsive column class
], style={"height": "100vh", "background-color": "#f8f9fa"})  # Set the overall background color and height of the page

# Start the Dash app server in debug mode, allowing for live updates on code changes
if __name__ == '__main__':
    app.run(debug=True)
