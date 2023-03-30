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
EXIT
```
followed by:
```bash
exit
```
