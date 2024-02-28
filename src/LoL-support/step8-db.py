import psycopg2
import json

# Connect to the PostgreSQL database
conn = psycopg2.connect(
    dbname="league",
    user="postgres",
    password="1234",
    host="127.0.0.1",
    port="5432"
)
cur = conn.cursor()

# Open the JSON file and load data
with open('final_data.json') as f:
    data = json.load(f)

# Iterate over the data and insert into the database
for record in data:
    champ_names = record['champion_name']
    # Remove "%" symbol and convert pick_rate to float
    pick_rate = float(record['pick_rate'].rstrip('%'))
    
    # Convert dictionaries to strings
    counters = json.dumps(record['counters'])
    synergies = json.dumps(record['synergy'])

    # Insert the data into the database
    cur.execute("INSERT INTO test_all (champ_names, pick_rate, counters, synergies) VALUES (%s, %s, %s, %s)", 
                (champ_names, pick_rate, counters, synergies))



# Commit the transaction and close the cursor/connection
conn.commit()
cur.close()
conn.close()
