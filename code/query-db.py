import mariadb
import sys
import getpass


try:
	conn = mariadb.connect(
		user="W11-TOPPLAB23",
		password=getpass.getpass(prompt='Database user password: '),
		host="10.16.0.101", #Nebula's relational ip!
		port=3306,
		database="tag_server"
	)
except mariadb.Error as e:
    print(f"Error connecting to MariaDB Platform: {e}")
    sys.exit(1)
	
	
	
cur = conn.cursor()
query = "SELECT * FROM tags"
value = ()
cur.execute(query,value)

for uid, uuid in cur:
    print(f"uid: {uid} uuid: {uuid}")

conn.commit()

cur.close()
conn.close()
