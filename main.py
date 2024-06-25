import psycopg2
import json
import plotly.express as px
import pandas as pd

connection = psycopg2.connect(host="localhost", 
                        dbname="bevoelkerungstudierende", 
                        user="postgres", 
                        password="1234", 
                        port=5432)

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
SELECT b.bundesland, b.insgesamt, h.studierende, 
       (h.studierende::FLOAT / b.insgesamt) * 100 AS prozentsatz
FROM bevoelkerung b
JOIN hochschulen h ON b.bundesland = h.bundesland;
"""

#df = pd.read_sql_query(query, connection)


# connection beenden
connection.commit()
cursor.close()
connection.close()


# heatmap erstellen
#import plotly.express as px

#fig = px.density_heatmap(df, x='bundesland', y='prozentsatz',
#                         title='Prozentsatz der Studierenden in jedem Bundesland',
#                         labels={'prozentsatz': 'Prozentsatz der Studierenden', 'bundesland': 'Bundesland'},
#                         color_continuous_scale=px.colors.sequential.Viridis)

#fig.show()

"""
SELECT hochschulen.bundesland, SUM(hochschulen.studierendenanzahl) AS gesamtstudierende, bevoelkerung.insgesamt
FROM hochschulen, bevoelkerung
WHERE hochschulen.bundesland = bevoelkerung.bundesland
GROUP BY bundesland
"""