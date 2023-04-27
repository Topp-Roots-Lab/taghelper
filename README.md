# taghelper
This is a collection of scripts that provide various functions to interact with a Mariadb database that contains sample barcode strings. The database is currently hosted on nebula, although this can be modified in the future. 

These tools are customized to the needs of the Topp Lab in 2023 but should be easily modifed to fit future changes.

## Installation

**Dependencies**

- python (3.7.4+)

```bash
pip install -r requirements.txt
```

## Configuration
### Adding new computers to mariadb
Any computer that will run these scripts needs to be recognized by the db. You must create a database user for each computer before attempting to run the scripts.

Check your computer's current ip address. You can do this by running 

```bash
ipconfig
```
on windows or
```bash
ifconfig
```
on linux. Use ssh to connect to the computer or server hosting the database.

```bash
ssh [hostname]@[hostip]
```

Open the mariadb configuration console.

```bash
sudo mariadb
```

Run the following SQL queries to add a new user.

```sql
CREATE USER '[the computer being added's username]'@'[the computer being added's ip]' IDENTIFIED BY '[password]';
GRANT ALL PRIVILEGES ON [database_name].* TO '[the computer being added's username]'@'[the computer being added's ip]';
FLUSH PRIVILEGES;
```
You can verify the new user's existance with:
```sql
SELECT User, Host FROM mysql.user;
```
Exit the database by typing:
```sql
EXIT;
```
followed by:
```bash
exit
```

Verify that the scripts are now functional on this computer by running the query-db.py script.
```bash
python query-db.py
```
### Accessing a database on a different server than default (Nebula).
The tagserver is currently hosted on Nebula. If you have moved the database to another host and want to change the scripts to access this host instead, you need to update the ip and hostname in the config.

Open id-upload.py (or whichever script you are trying to reconfigure) in a text editor.

Locate the try/except block towards the top of the page. If the script you are in doesn't have one that looks like this, it doesn't need to be reconfigured.
```python
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
```
This part is fairly self-explanatory. Update the username field to the new host's username, the host field to the new host's ip address, and the database field to the new host's database for tags (if changed).

## How do I use ___.py?
### Using id-upload.py
id-upload.py is the main script used to upload tags and generate ids. Here's how to use it :)

1. Open the command line and navigate to the directory containing the script by using
```bash
cd [directory name]
```
2. Run the script by typing
```bash
python id-upload.py
```
3. You will be prompted for the database password. Enter it in the command line and press enter.
4. Click the big "browse" button at the top to open a file explorer in which you will locate and open the excel sheet you plan to use.
![image](https://user-images.githubusercontent.com/100446167/234915732-d10afe90-064c-43df-9977-1aeaff7dbaa1.png)

