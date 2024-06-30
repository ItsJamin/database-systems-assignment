import psycopg2
import json
import plotly.express as px
import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output

geojson_path = 'assets/geojson_germany.geo.json'

db_params = {
    'dbname': 'bevoelkerungstudierende',
    'user': 'postgres',
    'password': '1234',
    'host': 'localhost',
    'port': 5432
}

#---------------------Connection zur Database und Daten abholen---------------------#

connection = psycopg2.connect(**db_params)

cursor = connection.cursor()

# Erstelle die Table bevoelkerung
cursor.execute("""CREATE TABLE IF NOT EXISTS bevoelkerung (
               region_id INT,
               bundesland VARCHAR(255),
               insgesamt INT,
               male INT,
               female INT,
               PRIMARY KEY(bundesland)
               );   
               """)

cursor.execute("""CREATE TABLE IF NOT EXISTS hochschulen (
               hochschulkurzname VARCHAR(100),
               hochschulname VARCHAR(255),
               hochschultyp VARCHAR(100),
               traegerschaft VARCHAR(100),
               bundesland VARCHAR(255),
               anzahlStudierende INTEGER,
               gruendungsjahr INTEGER,
               promotionsrecht VARCHAR(255),
               habilitationsrecht VARCHAR(255),
               strasse VARCHAR(255),
               postleitzahl VARCHAR(20),
               ort VARCHAR(100),
               homePage VARCHAR(255),
               CONSTRAINT fk_bundesland
                FOREIGN KEY(bundesland) 
                REFERENCES bevoelkerung(bundesland)
               );
               """)

cursor.execute("""CREATE TABLE IF NOT EXISTS Abschlussquote (
               region_id INT,
               bundesland VARCHAR(255),
               abschlussquotehochschulreife FLOAT,
               CONSTRAINT fk_bundesland
                FOREIGN KEY(bundesland) 
                REFERENCES bevoelkerung(bundesland)
               );   
               """)


query = """
SELECT 
    hochschulen.bundesland, 
    SUM(hochschulen.anzahlStudierende) AS gesamtstudierende, 
    SUM(bevoelkerung.insgesamt) AS gesamteinwohner,
    MAX(Abschlussquote.abschlussquotehochschulreife) AS abschlussquotehochschulreife
FROM hochschulen
JOIN bevoelkerung ON hochschulen.bundesland = bevoelkerung.bundesland
JOIN Abschlussquote ON hochschulen.bundesland = Abschlussquote.bundesland
GROUP BY hochschulen.bundesland
"""

cursor.execute(query)

rows = cursor.fetchall()
col_names = [desc[0] for desc in cursor.description]

# Verbindung beenden
connection.commit()
cursor.close()
connection.close()

#---------------------Auf dem Dataframe arbeiten---------------------#

# Lade GeoJSON
with open(geojson_path) as f:
    geojson_data = json.load(f)

# Erstelle DataFrame
df = pd.DataFrame(rows, columns=col_names)
df['Studierende in %'] = (df['gesamtstudierende'] / df['gesamteinwohner']) * 100
df['Studierende in %'] = round(df['Studierende in %'], 2)
df['Hochschulreife Abschlussquote in %'] = df['abschlussquotehochschulreife']
converted_df = df[['bundesland', 'Studierende in %', 'Hochschulreife Abschlussquote in %']]

#---------------------Dash-App---------------------#
app = dash.Dash(__name__)

app.layout = html.Div([
    # Filterbox für Bundesländer
    dcc.Dropdown(
        id='bundesland-dropdown',
        options=[{'label': bundesland, 'value': bundesland} for bundesland in converted_df['bundesland']],
        value=[],
        multi=True,
        placeholder="Select Bundesland"
    ),
    # Switch zwischen Ansicht welcher Metrik
    dcc.RadioItems(
        id='metric-radio',
        options=[
            {'label': 'Studierende pro Einwohner', 'value': 'Studierende in %'},
            {'label': 'Abschlussquote Hochschulreife', 'value': 'Hochschulreife Abschlussquote in %'}
        ],
        value='Studierende in %',
        labelStyle={'display': 'inline-block'}
    ),
    dcc.Graph(id='choropleth-graph')
])

@app.callback(
    Output('choropleth-graph', 'figure'),
    [Input('bundesland-dropdown', 'value'), Input('metric-radio', 'value')]
)
def update_figure(selected_bundeslaender, selected_metric):
    filtered_df = converted_df
    if selected_bundeslaender:
        filtered_df = converted_df[converted_df['bundesland'].isin(selected_bundeslaender)]
    
    colorscale = 'brwnyl' if selected_metric == 'Studierende in %' else 'viridis'
    range_color = (0.00, 1.00) if selected_metric == 'Studierende in %' else (0, 100)
    
    fig = px.choropleth(
        filtered_df,
        geojson=geojson_data,
        locations='bundesland',
        featureidkey='properties.name',
        color=selected_metric,
        color_continuous_scale=colorscale,
        range_color=range_color,
        hover_data=['Hochschulreife Abschlussquote in %'] if selected_metric == 'Studierende in %' else ['Studierende in %']
    )
    
    fig.update_layout(
        coloraxis_colorbar=dict(
            title="Studierende pro Einwohneranzahl" if selected_metric == 'Studierende in %' else "Abschlussquote Hochschulreife",
            tickvals=[0.0, 0.2, 0.4, 0.60, 0.8, 1.00] if selected_metric == 'Studierende in %' else [0, 20, 40, 60, 80, 100],
            ticktext=["0.00%", "0.20%", "0.40%", "0.60%", "0.80%", "1.00%"] if selected_metric == 'Studierende in %' else ["0%", "20%", "40%", "60%", "80%", "100%"],
        ),
        geo=dict(
            fitbounds="locations",
            visible=False
        )
    )
    
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)
