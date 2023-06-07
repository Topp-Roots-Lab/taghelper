'''
Inserts a single value from into a single table from command line arguments
'''

import mariadb
import sys
import getpass


try:
	conn = mariadb.connect(
		user="topplab",
		password=getpass.getpass(prompt='Database user password: '),
		host="10.16.0.101", #Nebula's relational ip!
		port=3306,
		database="tag_server"
	)
except mariadb.Error as e:
    print(f"Error connecting to MariaDB Platform: {e}")
    sys.exit(1)
	

if len(sys.argv) <= 3:
	print("USAGE: insert-db.py [table to insert to] [col to insert to] [value to insert]")
	sys.exit(1)



try:
	
	cur = conn.cursor()
	query = f"INSERT INTO {sys.argv[1]} ({sys.argv[2]}) VALUES (?)"
	value = (sys.argv[3],)
	cur.execute(query,value)

	conn.commit()

	cur.close()
	conn.close()
except mariadb.Error as e:
    print(f"Error with arguments: {e}")
    sys.exit(1)
