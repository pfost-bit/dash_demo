import numpy as np
import pandas as pd
import requests
import json
import plotly.express as px
import plotly.figure_factory as ff
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

gss = pd.read_csv("https://github.com/jkropko/DS-6001/raw/master/localdata/gss2018.csv",
                 encoding='cp1252', na_values=['IAP','IAP,DK,NA,uncodeable', 'NOT SURE',
                                               'DK', 'IAP, DK, NA, uncodeable', '.a', "CAN'T CHOOSE"])

mycols = ['id', 'wtss', 'sex', 'educ', 'region', 'age', 'coninc',
          'prestg10', 'mapres10', 'papres10', 'sei10', 'satjob',
          'fechld', 'fefam', 'fepol', 'fepresch', 'meovrwrk'] 
gss_clean = gss[mycols]
gss_clean = gss_clean.rename({'wtss':'weight', 
                              'educ':'education', 
                              'coninc':'income', 
                              'prestg10':'job_prestige',
                              'mapres10':'mother_job_prestige', 
                              'papres10':'father_job_prestige', 
                              'sei10':'socioeconomic_index', 
                              'fechld':'relationship', 
                              'fefam':'male_breadwinner', 
                              'fehire':'hire_women', 
                              'fejobaff':'preference_hire_women', 
                              'fepol':'men_bettersuited', 
                              'fepresch':'child_suffer',
                              'meovrwrk':'men_overwork'},axis=1)
gss_clean.age = gss_clean.age.replace({'89 or older':'89'})
gss_clean.age = gss_clean.age.astype('float')

HEAD_COLORS = [
    '#e41a1c', '#377eb8', '#4daf4a', '#984ea3',
    '#ff7f00', '#ffff33', '#a65628', '#f781bf', '#999999'
]

HEAD_SYMBOLS = ['circle', 'square', 'triangle-up', 'diamond']

STEM_COLOR = ['grey', 'black', 'white']

DOMAIN_COLORS = [
    '#8dd3c7', '#ffffb3', '#bebada', '#fb8072',
    '#80b1d3', '#fdb462', '#b3de69', '#fccde5',
    '#d9d9d9', '#bc80bd', '#ccebc5', '#ffed6f'
]

def description():
    return 'Dash app to explore gender wage gap.'

def header_colors():
    return {
        'bg_color': '#0D1A51',
        'font_color': '#FFFFFF',
        'light_logo': True
    }

gender_markdown = '''
### Gender Wage Gap

The gender wage gap, the difference in pay between men's and women's earnings, has been discussed for a long time. Despite the discussion, the gap has largely remained unchanged.  
> In 2022, American women typically earned 82 cents for every dollar earned by men. [- Pew Research Center](https://www.pewresearch.org/social-trends/2023/03/01/the-enduring-grip-of-the-gender-pay-gap/)  

This comes as a surprise given that women have outpaced men in educational attainment. The most longstanding hurdle is motherhood. Women are more likely to leave the workforce early and "lose out" on earnings.
'''

gss_markdown = '''
### About the GSS Survey

The [General Social Survey](https://gss.norc.org/us/en/gss/about-the-gss.html) (GSS) is a nationally representative survey of U.S. adults. It explains trends in opinions, attitudes, and behaviors. Recent surveys achieved over 4,100 completions.

Key data: age, sex, income, education, and opinions on social issues.  
Example:
> "A working mother can establish just as warm and secure a relationship with her children as a mother who does not work."
'''

question_markdown = '''
> It is much better for everyone involved if the man is the achiever outside the home and the woman takes care of the home and family.                     
'''

income_box = px.box(gss_clean, x='sex', y='income', color='sex',
                    labels={'income':'Income'},
                    height=600,width=600)
income_box.update_layout(showlegend=False)

job_box = px.box(gss_clean, x='sex', y='job_prestige', color='sex',
                 labels={'job_prestige':'Job Prestige'},
                 height=600,width=600)
job_box.update_layout(showlegend=False)

gss_clean['male_breadwinner'] = gss_clean['male_breadwinner'].astype('category')
gss_clean['male_breadwinner'] = gss_clean['male_breadwinner'].cat.reorder_categories(['strongly agree', 'agree', 'disagree', 'strongly disagree'])

gss_bar = gss_clean.groupby(['sex','male_breadwinner'],observed=False).size()
gss_bar = gss_bar.reset_index()
gss_bar = gss_bar.rename({0:'count'},axis=1)

fig_bar = px.bar(gss_bar, x='male_breadwinner', y='count', color='sex', 
             labels={'count':'Number of Respondents',
                     'male_breadwinner':'Level of Response to the Male Breadwinner Question'},
             text='count',
             barmode='group',
             height=600,width=800)


gss_clean['education'] = pd.cut(
    gss_clean['education'],
    bins=[0, 8, 10, 12, 15, 16, 20],
    labels=[
        'No High School',
        'Some High School',
        'High School Graduate',
        'Some College (No Degree)',
        'College Graduate',
        'Postgraduate Degree'
    ],
    right=True,
    include_lowest=True
)

gss_clean['education'] = gss_clean['education'].astype('category')
gss_clean['education'] = gss_clean['education'].cat.reorder_categories(
    [
        'No High School',
        'Some High School',
        'High School Graduate',
        'Some College (No Degree)',
        'College Graduate',
        'Postgraduate Degree'
    ],
    ordered=True
)

gss_clean['satjob'] = gss_clean['satjob'].astype('category')
gss_clean['satjob'] = gss_clean['satjob'].cat.reorder_categories(
        [
            'very dissatisfied',
            'a little dissat',
            'mod. satisfied',
            'very satisfied'
        ]
)

gss_clean['relationship'] = gss_clean['relationship'].astype('category')
gss_clean['relationship'] = gss_clean['relationship'].cat.reorder_categories(
        [
            'strongly disagree',
            'disagree',
            'agree',
            'strongly agree'
        ]
)

gss_clean['child_suffer'] = gss_clean['child_suffer'].astype('category')
gss_clean['child_suffer'] = gss_clean['child_suffer'].cat.reorder_categories(
    [
        'strongly disagree',
        'disagree',
        'agree',
        'strongly agree'
    ]
)

gss_clean['men_overwork'] = gss_clean['men_overwork'].astype('category')
gss_clean['men_overwork'] = gss_clean['men_overwork'].cat.reorder_categories(
    [
        'strongly disagree',
        'disagree',
        'neither agree nor disagree',
        'agree',
        'strongly agree'
    ]
)


question_descriptions = {
    'satjob': "On the whole, how satisfied are you with the work you do?",
    'relationship': "Agree or disagree: A working mother can establish just as warm and secure a relationship with her children as a mother who does not work.",
    'male_breadwinner': "Agree or disagree: It is much better for everyone involved if the man is the achiever outside the home and the woman takes care of the home and family.",
    'men_bettersuited': "Agree or disagree: Most men are better suited emotionally for politics than are most women.",
    'child_suffer': "Agree or disagree: A preschool child is likely to suffer if his or her mother works.",
    'men_overwork': "Agree or disagree: Family life often suffers because men concentrate too much on their work."
}



app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div([
    html.Div([
        html.Div([
            html.H1("Gender Wage Gap Dashboard"),
            dcc.Markdown(gender_markdown),
            html.Hr(),
            dcc.Markdown(gss_markdown)
        ], className='sidebar'),

        html.Div([  
            html.H2("Visualizations"),            
            html.Hr(),
            html.H3("Response to the Male Breadwinner Question"),
            dcc.Markdown(question_markdown),
            html.Div([
                dcc.Graph(figure=fig_bar, style={"display": "inline-block", "width": "80%"})
            ], style={"textAlign": "center"}),
            dcc.Markdown("Even though men and women generally agree, that either man or women can be the primary breadwinner, women still make less money on average."),
            html.Hr(),
            html.Div([
                html.Div([
                    html.H3("Income by Gender"),
                    dcc.Graph(figure=income_box)
                ], style={'width': '48%', 'margin-right': '2%'}),
                
                html.Div([
                    html.H3("Job Prestige by Gender"),
                    dcc.Graph(figure=job_box)
                ], style={'width': '48%'})
            ], style={'display': 'flex', 'flex-wrap': 'wrap', 'justify-content': 'space-between'}),
            dcc.Markdown("Event though men and women have similar job prestige, women still make less money on average."),
            html.Hr(),
        html.Div([
            html.Div([
            
            html.H6("x-axis feature"),
            dcc.Dropdown(id='x-axis',
                         options=[{'label':i, 'value':i} for i in ['satjob', 'relationship', 'male_breadwinner', 'men_bettersuited', 'child_suffer', 'men_overwork']],
                         value='child_suffer'),
            html.H6("group by feature"),
            dcc.Dropdown(id='group-by',
                         options=[{'label':i, 'value':i} for i in['sex', 'region', 'education']],
                         value='sex')
        
            ], style={'width': '25%'}),
            
            html.Div([
                
                dcc.Graph(id='barplots'),
                html.Div([
                    html.Div(id='question-description', style={'margin': '20px 0', 'fontSize': '16px'})
                ],style={'display': 'flex', 'justifyContent': 'center'}),       
            ], style={'width': '70%'})
            ], style={'display': 'flex', 'flex-wrap': 'wrap', 'justify-content': 'space-between'})


        ], className='content')
    ], className='main-container')
])

@app.callback(Output(component_id="barplots",component_property="figure"), 
                  [Input(component_id='x-axis',component_property="value"),
                   Input(component_id='group-by',component_property="value")])

def make_figure(x,color):
    gss_bar_plot = gss_clean.groupby([color,x],observed=False).size()
    gss_bar_plot = gss_bar_plot.reset_index()
    gss_bar_plot = gss_bar_plot.rename({0:'count'},axis=1)
    fig =  px.bar(
        gss_bar_plot, 
        x=x, 
        y='count', 
        color=color, 
        labels={'count':'Number of Respondents'},
        barmode='group',
        height=600,width=800)
    return fig

@app.callback(
    Output('question-description', 'children'),
    Input('x-axis', 'value')
)
def update_description(selected_x):
    return question_descriptions.get(selected_x, "Select a question to see its description.")


# Custom CSS for layout
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>Dashboard</title>
        {%favicon%}
        {%css%}
<style>
    body {
        margin: 0;
        font-family: Arial, sans-serif;
    }
    .main-container {
        display: flex;
        height: 100vh;
        overflow: hidden;
    }
    .sidebar {
        width: 30%;
        background-color: #f8f8f8;
        padding: 20px;
        overflow-y: auto;
        box-sizing: border-box;
        border-right: 1px solid #ddd;
    }
    .content {
        width: 70%;
        padding: 20px;
        overflow-y: scroll;
        box-sizing: border-box;
        background-color: white;
    }
    dcc-graph {
        width: 100% !important;
    }
</style>

    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''



if __name__ == '__main__':
    app.run(debug=True, port=8051)
