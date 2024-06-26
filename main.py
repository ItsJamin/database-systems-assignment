import psycopg2
import json
import plotly.express as px
import pandas as pd

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

# erstelle die table bevoelkerung
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


query = """
SELECT hochschulen.bundesland, SUM(hochschulen.anzahlStudierende) AS gesamtstudierende, SUM(bevoelkerung.insgesamt) AS gesamteinwohner
FROM hochschulen, bevoelkerung
WHERE hochschulen.bundesland = bevoelkerung.bundesland
GROUP BY hochschulen.bundesland
"""

cursor.execute(query)

rows = cursor.fetchall()
col_names = [desc[0] for desc in cursor.description]


# connection beenden
connection.commit()
cursor.close()
connection.close()



#---------------------Auf dem Dataframe arbeiten---------------------#

df = pd.DataFrame(rows, columns=col_names)

df['prozentsatz'] = (df['gesamtstudierende'] / df['gesamteinwohner']) * 100

# Prozente formattieren
df['prozentsatz'] = round(df['prozentsatz'],2)

converted_df = df[['bundesland', 'prozentsatz']]
print(converted_df)

#---------------------Heatmap erstellen---------------------#


with open(geojson_path) as f:
    geojson_data = json.load(f)


# Choropleth Heatmap

fig = px.choropleth(
    converted_df,
    geojson=geojson_data,
    locations='bundesland',
    featureidkey='properties.name', # verbindet 'bundesland' mit den geojson regionen
    color='prozentsatz', # welche Daten sollen visualisiert werden
    color_continuous_scale='brwnyl', # andere Scales: agsunset, viridis
    range_color=(0.00, 1.00),
    labels={'prozentsatz':'Prozentsatz der Studierenden pro Bundesland'}
)

fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
fig.show()
