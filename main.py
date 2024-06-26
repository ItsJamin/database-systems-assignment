import psycopg2
import json
import plotly.express as px
import pandas as pd

#---------------------Connection zur Database und Daten abholen---------------------#

db_params = {
    'dbname': 'bevoelkerungstudierende',
    'user': 'postgres',
    'password': '1234',
    'host': 'localhost',
    'port': 5432
}

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

df['percentage'] = (df['gesamtstudierende'] / df['gesamteinwohner']) * 100

# Format the percentage
df['percentage'] = df['percentage'].map(lambda x: f'{x:.2f}%')

# Display the desired output
result = df[['bundesland', 'percentage']]
print(result)

# heatmap erstellen
#import plotly.express as px

#fig = px.density_heatmap(df, x='bundesland', y='prozentsatz',
#                         title='Prozentsatz der Studierenden in jedem Bundesland',
#                         labels={'prozentsatz': 'Prozentsatz der Studierenden', 'bundesland': 'Bundesland'},
#                         color_continuous_scale=px.colors.sequential.Viridis)

#fig.show()
