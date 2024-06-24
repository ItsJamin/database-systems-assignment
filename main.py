import psycopg2

connection = psycopg2.connect(host="localhost", 
                        dbname="bevoelkerungstudierende", 
                        user="postgres", 
                        password="1234", 
                        port=5432)

cursor = connection.cursor()

# do smth


# end of connection
connection.commit()
cursor.close()
connection.close()

