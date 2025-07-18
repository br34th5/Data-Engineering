import psycopg2
from config import config

# Connect to the PostgreSQL database
def connect():
    connection = None
    try:
        params = config()
        print("connecting to postgresql database ...")
        connection = psycopg2.connect(**params)

        #create a cursor
        crsr = connection.cursor()
        print("postgresql database version:  ")
        crsr.execute('SELECT version()')
        db_version = crsr.fetchone()
        print(db_version)
        #close cursor
        crsr.close()
    except(Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        # Close the connection
        if connection is not None:
            connection.close()
            print('database connection terminated')

if __name__ == '__main__':
    connect()