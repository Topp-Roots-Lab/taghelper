# Taghelper 2.0
**These instructions will become effective soon but please refer to Taghelper 1.0 below this section until the transfer.**

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
Update the username field to the new host's username, the host field to the new host's ip address, and the database field to the new host's database for tags (if changed).

### Logging into Adminer
The database manager, Adminer, is currently set up on Nebula to help manage this database. This is how you can log into Adminer from any computer on the same network as Nebula.

In the browser of your choice (this has only been tested in chrome though), navigate to 
```
[ipaddress of server]/adminer
```
Currently this is 
```
http://10.16.0.101/adminer
```

You should see a screen that looks like this:

![image](https://github.com/Topp-Roots-Lab/taghelper/assets/100446167/221a4650-4531-4f09-93f3-e48da17b7c7d)

Keep localhost the same as it is referring to the localhost of the ip address, not your machine.

Fill in your login details and click login. Database is an optional field and should probably usually be left blank to access the entire server.

### Adding new tables (for new sample types) to mariadb.
The database currenty has a central table for basic information, as well as tables for biomass, core wholes, core segments, and crowns. You will likely need to add more tables to accomadate new projects in the future. This database was designed to be flexible and easily expandable.

Log into Adminer (following the steps above). Select the database you want to add tables to (currently named "Samples").

![image](https://github.com/Topp-Roots-Lab/taghelper/assets/100446167/91ad4c46-e91e-4320-9364-13c7874aa7cb)

Choose the "Create Table" option from the menu.

![image](https://github.com/Topp-Roots-Lab/taghelper/assets/100446167/220ce64c-45bf-4f3d-a71c-7edac55a15de)



# Taghelper 1.0
***WARNING***
**These instructions will be depreciated after the transfer to Taghelper 2.0**


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

5. Click the big "browse" button at the top to open a file explorer in which you will locate and open the excel sheet you plan to use.
![image](https://user-images.githubusercontent.com/100446167/234915732-d10afe90-064c-43df-9977-1aeaff7dbaa1.png)
![image](https://user-images.githubusercontent.com/100446167/234927510-1474c5e9-0c6f-43aa-98d5-5d504a44497b.png)


6. Go into your workbook and double click on the sheet name in the tab at the bottom. Use Ctl+C to copy this text exactly. Paste it into the area that says "Sheet name".
![image](https://user-images.githubusercontent.com/100446167/234917856-f1927828-6e15-491c-98e5-c0593ba973f0.png)
![image](https://user-images.githubusercontent.com/100446167/234918246-7078d5ec-330e-4f0c-8196-fea55e2cb70b.png)

7. Find the col number containing your barcode strings by counting the columns, starting with 1 from the left. Type this number into the appropriate box.
![image](https://user-images.githubusercontent.com/100446167/234919748-55731665-defa-4564-9762-f29158bf81cb.png)
![image](https://user-images.githubusercontent.com/100446167/234920042-604aac91-435e-45f5-8ffa-3f6004c197f8.png)

8. Find the first row number containing **ACTUAL DATA** and enter this into the next area.
![image](https://user-images.githubusercontent.com/100446167/234920789-4bdbe593-b70d-4505-bb75-9e0a49c4ad01.png)
![image](https://user-images.githubusercontent.com/100446167/234920886-9132547f-4c0b-4162-bdcb-3840e49e9ca0.png)

9. Find the last row number containing data. **MAKE SURE THERE ARE NO EMPTY BOXES IN BETWEEN THE FIRST AND LAST ROW IN THE SELECTED COL.**
![image](https://user-images.githubusercontent.com/100446167/234921512-36aba0b1-b5dc-4b44-95fc-df5631d8b45a.png)
![image](https://user-images.githubusercontent.com/100446167/234921600-9b5141d1-ac92-49e0-a3a0-3ee9d92fe955.png)

10. **MAKE SURE YOU CLOSE THE EXCEL DOCUMENT BEFORE UPLOADING!!**

11. Click "Upload". Monitor the console and be sure that the "Reading Row: x" counter goes until the last row number. 
![image](https://user-images.githubusercontent.com/100446167/234922662-31f76b61-b427-48aa-a2ac-53aae645726d.png)

12. Find the col number for UIDs in much the same way as finding the col number for the barcodes. Count columns starting from the left. Enter the value in the appropriate box. 
![image](https://user-images.githubusercontent.com/100446167/234925215-813f460a-5d5f-489a-89b8-ae84cfdd20bf.png)
![image](https://user-images.githubusercontent.com/100446167/234925371-c34b1e1e-3f15-409f-9bc1-ea99df91bd83.png)

13. Find the first row number to save UIDs in. **THIS SHOULD BE THE SAME AS THE FIRST ROW OF BARCODE VALUES!** Enter it in the correct box.
![image](https://user-images.githubusercontent.com/100446167/234926272-908e6869-1599-4df9-b938-8be34d23b06b.png)
![image](https://user-images.githubusercontent.com/100446167/234926384-6d40bb61-3e76-4870-b26b-fee752bd22b6.png)

14. **MAKE SURE YOU CLOSE THE EXCEL DOCUMENT BEFORE WRITING!!**

15. Click "Write". Monitor the console and wait for the message "Write Successful" to be printed. 

16. Open your document and make sure that the numbers seem to be consistent. You can use the script 
```bash
python query-db.py
```
to make sure that all values are the same in the database.

17. You're done! I hope that was easy enough to understand and follow.



