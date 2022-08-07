import dash
import plotly.graph_objects as go
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Output, Input, State
import dash_table
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
import pandas as pd

from JutubCommentAnalysys.sent_analysis import SentimentAnalyzer
from JutubCommentAnalysys.youtube_comments import YouTubeComments

sentiment_analyzer = SentimentAnalyzer()
yt_comms = YouTubeComments()


def colors_list(points_list: list) -> list:
    colors = []
    for points in points_list:
        if points >= 0.05:
            colors.append("green")
        if -0.05 < points < 0.05:
            colors.append("blue")
        if points <= -0.05:
            colors.append("red")

    return colors


external_css = [dbc.themes.BOOTSTRAP, "static/reset.css"]
external_js = ["https://cdnjs.cloudflare.com/ajax/libs/materialize/0.100.2/js/materialize.min.js"]

app = dash.Dash(
    "YouTubeCommentsAnalysisApp",
    external_stylesheets=external_css,
    external_scripts=external_js
)

PLOTLY_LOGO = "https://images.plot.ly/logo/new-branding/plotly-logomark.png"
app.layout = html.Div([
    dbc.Navbar(
        dbc.Container(
            [
                html.A(
                    dbc.Row(
                        [
                            dbc.Col(html.Img(src=PLOTLY_LOGO, height="30px"), width="20px"),
                            dbc.Col(dbc.NavbarBrand("YouTube Comments Analysis", className="ms-2")),
                        ],
                        align="center",
                        className="g-0",
                    ),
                    href="https://plotly.com",
                    style={"textDecoration": "none"},
                ),
                dbc.NavbarToggler(id="navbar-toggler", n_clicks=0),

            ]
            , style={"width": "2500px", "margin-right": "1000px"}),
        color="dark",
        dark=True,
    ),
    dbc.Row([
        dbc.Card(
            dbc.CardBody([
                dbc.Row([
                    html.Div([
                        html.H6("URL: "),
                        dbc.Input(id="url_input", type="text", value="https://www.youtube.com/watch?v=WLhaPQvCExs",
                                  style={"width": "900px", "height": "40px", "margin-right": "30px"}),
                    ]),
                    html.Div([
                        html.H6("Max comments number: "),
                        dbc.Input(id="max_res_input", type="number", value="200", style={"width": "250", "height": "40px"}),
                    ]),

                    dbc.Button("Search", id="submit", style={'width': '150px', 'fontSize': '17px', "margin-left": "30px", "margin-top": "26px"})
                ], justify="center", align="center", className="h-50"),
            ], style={"width": "87rem"})
        ),
        html.H4(id="error_msg"),
        dbc.Card(
            dbc.CardBody([
                dcc.Graph(id="sentiments_graph", style={"height": "420px", "margin-bottom": "10px"}),
            ], style={"width": "87rem", "height": "28rem"})
            , style={"margin-top": "30px"}),
    ], align="center", justify="center", style={"margin-top": "60px"}),

    dbc.Row([
        dbc.Col([
            dbc.Card(
                dbc.CardBody([
                    html.H1("Comments",
                            style={"fontSize": "35px"}),
                    html.Div(id="table")
                ]),
            )

        ], width={"size": 6}, style={"height": "800px"}),
        dbc.Col([
            dbc.Card(
                dbc.CardBody([
                    html.H1("Sentiments percentage",
                            style={"fontSize": "35px"}),
                    dcc.Graph(id="pie_chart")
                ], className="lead")
            ),
            dbc.Card(
                dbc.CardBody([
                    html.H3("Chunk of information"),
                    html.P("This app has been made for analyzing YouTube comments in order to determinate whether"
                           " comments are positive, negative or neutral. It can help you with exploring feedback from comment section."
                           "Comments are taken from YouTube API and then analyzed by Vader Sentiment library.")
                               ])
                , style={"margin-top": "30px"})

        ], style={"margin-left": "4px", "height": "800px"}, width={"size": 5})
    ], align="center", justify="center", style={"margin-top": "30px", "margin-bottom": "15px"}),
    dbc.Row([
        dbc.Card(
            [
                dbc.CardBody(
                    [
                        html.H4("Not fancy footer", className="card-title"),
                        # html.P("This is some card text", className="card-text"),
                    ]
                    , style={"background-color": "#343a40", "text-align": "center", "color": "white"}),
                dbc.CardFooter("@YouTubeCommentsAnalysis", style={"text-align": "center", "color": "white",
                                                                  "background-color": "#2f3e46"}),
            ],
            style={"width": "100%"})
    ], align="center", justify="center", style={"margin-top": "50px"}),
], style={"background-color": "#dee2e6"})


@app.callback(
    [Output("sentiments_graph", "figure"),
     Output("table", "children"),
     Output("pie_chart", "figure"),
     Output("error_msg", "children"),
     ],
    [Input("submit", "n_clicks")],
    [State('url_input', 'value'),
     State('max_res_input', 'value'),
     ],
)
def update(n, url, max_comments):
    if url is None or url == "" or max_comments is None or max_comments == "":
        raise PreventUpdate
    else:
        comments_dict = yt_comms.get_comments(video_url=url, max_results=int(max_comments))
        scatter_title = "Video comments data"
        if comments_dict:
            df = pd.DataFrame.from_dict(comments_dict)
            df['Date'] = pd.to_datetime(df['Date']).dt.tz_localize(None)

            analyzed_sents_list = df['Comments'].apply(lambda x: sentiment_analyzer.analyze_sent(x)).to_list()
            # sent_emotions_list = df['Comments'].apply(lambda x: sentiment_analyzer.get_emotion_info(x)).to_list()

            # rozdzielanie na punkty i klase
            classes_list = []
            points_list = []
            for analyzed_sent in analyzed_sents_list:
                classes_list.append(analyzed_sent[0])
                points_list.append(analyzed_sent[1])

            # tworzenie kolumn
            df['Class'] = classes_list
            df['Points'] = points_list

            x = df['Date']
            y = df['Points']

            data = go.Scatter(
                x=x,
                xaxis="x",
                y=y,
                yaxis="y",
                name="day_range_graph",
                mode="markers",
                marker_color=colors_list(points_list),
                marker=dict(size=10)

            )

            fig = {"data": [data], 'layout': go.Layout(
                title=scatter_title,
                yaxis=dict(title='Points')
            )}

            table_df = df[['Date', 'Comments', 'Points']]
            table = dash_table.DataTable(
                data=table_df.to_dict("records"),
                columns=[{"id": c, "name": c} for c in table_df.columns],
                style_table={'height': '627px', 'overflowY': 'auto'},
                style_as_list_view=True,
                page_action='native',
                page_current=0,
                page_size=10,
                style_header={
                    # "backgroundColor": "#212529",
                    "border": "2px solid black"
                },
                style_cell={
                    "whiteSpace": "normal",
                    "textAlign": "left",
                    "height": 80,
                    # "color": colors["font"],
                    "border": "2px solid black"
                },
                style_cell_conditional=[
                    {"if": {"column_id": "Date"},
                     "width": "25%"},
                    {"if": {"column_id": "Points"},
                     "width": "10%"},
                    {"if": {"column_id": "Comments"},
                     "maxWidth": 200},
                ],
                style_data_conditional=[
                    {
                        "if": {
                            "filter_query": "{Points} > -0.05 and {Points} < 0.05",
                            "column_id": ["Date", "Comments", "Points"]

                        },
                        "backgroundColor": "#335c67"
                    },
                    {
                        "if": {
                            "filter_query": "{Points} > 0.05",
                            "column_id": ["Date", "Comments", "Points"]
                        },
                        "backgroundColor": "#386641"
                    },
                    {
                        "if": {
                            "filter_query": "{Points} < -0.05",
                            "column_id": ["Date", "Comments", "Points"]
                        },
                        "backgroundColor": "#8d0801"
                    },
                ]
            )

            pie_chart = go.Pie(
                labels=["Pos", "Neg", "Neut"],
                values=[df['Class'][df['Class'] == "pos"].count(),
                        df['Class'][df['Class'] == "neg"].count(),
                        df['Class'][df['Class'] == "neu"].count()],
                name="Sentiments_Pie_Chart",
                marker={
                    "colors": [
                        "#386641",
                        "#8d0801",
                        "#335c67",
                    ]
                }
            )

            data = [pie_chart]
            layout = go.Layout(
                # plot_bgcolor=colors["elements"],
                # paper_bgcolor=colors["elements"],
                # titlefont=dict(color=colors["font"]),
                margin=dict(t=50, l=30, r=0, b=0)
            )

            pie_fig = go.Figure(data=data, layout=layout)

            pie_fig.update_layout(
                titlefont=dict(size=35),
            )

            return fig, table, pie_fig, ""
        return {}, "", {}, "Video not found, try another one"


if __name__ == '__main__':
    app.run_server(debug=True)
