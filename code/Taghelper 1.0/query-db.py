import mariadb
import sys
import getpass
import os


try:
	conn = mariadb.connect(
		user=os.getlogin(),
		password=getpass.getpass(prompt='Database user password: '),
		host="10.16.0.101", #Nebula's relational ip!
		port=3306,
		database="testing"
	)
except mariadb.Error as e:
    print(f"Error connecting to MariaDB Platform: {e}")
    sys.exit(1)
	
	
	
cur = conn.cursor()
query = "SELECT * FROM biomass"
value = ()
cur.execute(query,value)
response = []

for t in cur:
    response += [t]
    print(t)
print(response)
for uid, uuid in response:
    print(f"uid: {uid} uuid: {uuid}")

conn.commit()

cur.close()
conn.close()
