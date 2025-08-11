import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, dcc, html
import dash_bootstrap_components as dbc

# Load Data
df = pd.read_csv("clean.csv")
pop_df = pd.read_excel("Population dataset.xlsx")

# Updated EAC countries list
eac_countries = ['Burundi', 'DRC', 'Kenya', 'Rwanda', 'South Sudan', 'Tanzania', 'Uganda', 'Somalia']

# 1. Global Crop Production Over Time
yearly_production = df[df['Element'] == 'Production'].groupby('Year')['Value'].sum().reset_index()
fig1 = px.line(yearly_production, x='Year', y='Value', title='Global Crop Production Over Time')
fig1.update_layout(yaxis_title='Total Production', height=500)
fig1.update_traces(line=dict(color='#006400'))

# 2. Global Crop Production by Category
category_production = df[df['Element'] == 'Production'].groupby('Category')['Value'].sum().reset_index().sort_values(by='Value')
fig2 = px.bar(
    category_production,
    y='Category',
    x='Value',
    orientation='h',
    title='Total Agricultural Production by Category (tonnes)',
    labels={'Value': 'Total Production (tonnes)'}
)
fig2.update_layout(height=500, margin=dict(l=200), xaxis_title='Total Production (tonnes)', yaxis_title='',
                   template='plotly_white', hovermode='y unified')
fig2.update_traces(marker_color='#006400', hovertemplate='%{x:,.0f} tonnes')

# 3. Global Crop Production by Country
country_production = df[df['Element'] == 'Production'].groupby('Country')['Value'].sum().reset_index()
fig3 = px.choropleth(country_production, locations='Country', locationmode='country names',
                     color='Value', color_continuous_scale='YlGn', title='Total Crop Production by Country')
fig3.update_layout(geo=dict(showframe=False, showcoastlines=False),
                   coloraxis_colorbar=dict(title="Production"), height=500)

# 4. Updated Crop Production in EAC Countries
eac_df = df[(df['Country'].isin(eac_countries)) & (df['Element'] == 'Production')]
eac_country_production = eac_df.groupby('Country')['Value'].sum().reset_index().sort_values(by='Value', ascending=False)
fig4 = px.bar(eac_country_production, x='Value', y='Country', orientation='h',
              title='Total Agricultural Production in EAC Countries (1990–2019)',
              labels={'Value': 'Total Production', 'Country': 'Country'})
fig4.update_traces(marker_color='darkgreen')
fig4.update_layout(yaxis={'categoryorder': 'total ascending'}, height=500)

# 5. Most Produced Crop Items in EAC
eac_items = eac_df.groupby('Category')['Value'].sum().reset_index().sort_values(by='Value', ascending=True)
fig5 = px.bar(eac_items, x='Value', y='Category', orientation='h',
              title='Most Produced Crop Category in EAC (1990–2019)',
              labels={'Value': 'Total Production', 'Category': 'Category'})
fig5.update_traces(marker_color='darkgreen')
fig5.update_layout(height=600, yaxis={'categoryorder': 'total ascending'})

# 6. Production per Capita in EAC
df_prod = df[df['Element'] == 'Production'].copy()
prod_sum = df_prod.groupby(['Country', 'Year'])['Value'].sum().reset_index()
prod_sum.rename(columns={'Value': 'Total_Production'}, inplace=True)
merged_df = pd.merge(prod_sum, pop_df, on=['Country', 'Year'], how='inner')
eac_prod = merged_df[merged_df['Country'].isin(eac_countries)].copy()
eac_prod['Production_per_Capita'] = eac_prod['Total_Production'] / eac_prod['Population']
fig6 = px.line(
    eac_prod,
    x='Year',
    y='Production_per_Capita',
    color='Country',
    title='Production per Capita in EAC Countries (1990–2019)',
    labels={'Production_per_Capita': 'Production per Capita (Tonnes)'}
)
fig6.update_layout(yaxis_title='Tonnes per Person', height=500, template='plotly_white')

# 7. Climate Trends in EAC
climate_df = df[(df['Year'] >= 1990) & (df['Year'] <= 2019)]
climate_trends = climate_df.groupby('Year')[['AvgTemp_C', 'TotalRainfall_mm']].mean().reset_index()
fig7 = go.Figure()
fig7.add_trace(go.Scatter(
    x=climate_trends['Year'],
    y=climate_trends['AvgTemp_C'],
    name='Avg Temperature (°C)',
    mode='lines+markers',
    line=dict(color='green')
))
fig7.add_trace(go.Scatter(
    x=climate_trends['Year'],
    y=climate_trends['TotalRainfall_mm'],
    name='Total Rainfall (mm)',
    mode='lines+markers',
    line=dict(color='royalblue'),
    yaxis='y2'
))
fig7.update_layout(
    title='Climate Trends in EAC (1990–2019)',
    xaxis=dict(title='Year'),
    yaxis=dict(title=dict(text='Avg Temperature (°C)', font=dict(color='green')), tickfont=dict(color='green')),
    yaxis2=dict(title=dict(text='Total Rainfall (mm)', font=dict(color='royalblue')),
                tickfont=dict(color='royalblue'), anchor='x', overlaying='y', side='right'),
    legend=dict(x=0.5, y=1.1, orientation='h'),
    template='plotly_white'
)

# Dash App
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Global Food Security and Agriculture Trends"

# Layout
app.layout = dbc.Container([
    html.H1("Global Food Security and Agriculture Trends Dashboard", className="header-title"),
    html.P("Food security remains a critical global issue, with over 700 million people facing hunger in 2022."
           "\n\nAgricultural productivity plays a key role but is challenged by climate variability and resource limits."
           "\n\nThis dashboard analyzes FAOSTAT data to explore trends and influencing factors on food production."
           "\n\nWe explore production trends, compare regions, and assess the relationship between population and agricultural productivity.",
           className="header-subtitle"),

    dbc.Tabs([
        dbc.Tab(label="Global Crop Production Trends", children=[
            html.H3("Global Crop Production Over Time", className="section-title"),
            dcc.Graph(figure=fig1),
            html.H3("Global Crop Production by Category", className="section-title"),
            dcc.Graph(figure=fig2),
            html.H3("Global Crop Production by Country", className="section-title"),
            dcc.Graph(figure=fig3)
        ]),

        dbc.Tab(label="East Africa Insights", children=[
            html.H3("Crop Production by EAC Country", className="section-title"),
            dcc.Graph(figure=fig4),
            html.H3("Most Produced Crop Categories in EAC", className="section-title"),
            dcc.Graph(figure=fig5),
            html.H3("Production per Capita in EAC", className="section-title"),
            dcc.Graph(figure=fig6),
            html.H3("Climate Trends in EAC", className="section-title"),
            dcc.Graph(figure=fig7)
        ]),

        dbc.Tab(label="Recommendations", children=[
            html.Div([
                html.H4("Key Recommendations", className="text-success"),
                html.Ul([
                    html.Li("In countries with declining per capita production, like Uganda, there’s a need to balance agricultural growth with population growth."),
                    html.Li("Countries should monitor rainfall and temperature trends when planning seasonal agriculture to reduce risks tied to climate shifts."),
                    html.Li("Continue supporting and optimizing the most productive crop categories (fruits & roots), as they form the backbone of regional output.")
                ])
            ], className="p-4")
        ]),

        dbc.Tab(label="Conclusion", children=[
            html.Div([
                html.H4("Summary of Findings", className="text-success"),
                html.Ul([
                    html.Li("Global crop production has increased steadily over the past decades."),
                    html.Li("Cereals remain the dominant crop category worldwide."),
                    html.Li("There are significant variations in production levels across EAC countries."),
                    html.Li("Production per capita provides deeper insights into food availability per person."),
                    html.Li("Climate trends such as rainfall and temperature must be monitored for future resilience.")
                ])
            ], className="p-4")
        ])
    ])
], fluid=True)

# Run the App
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8050)
