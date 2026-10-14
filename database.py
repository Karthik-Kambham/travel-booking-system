import mysql.connector

def get_connection():
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Karthik@12345",
        database="travel_booking"
    )

    return connection


connection = get_connection()

if connection.is_connected():
    print("MySQL Connected Successfully!")

connection.close()