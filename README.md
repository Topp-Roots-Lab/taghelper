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

Use ssh to connect to the computer or server hosting the database.

```bash
ssh [hostname]@[hostip]
```
