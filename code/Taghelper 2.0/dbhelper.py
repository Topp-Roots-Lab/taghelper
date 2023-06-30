def insertValue(dbTable,dbCol,value,con,cur):
    '''
    Inserts a single value to the connected database

    Parameters:
        str dbTable (name of table in connected database)
        str dbCol (name of col in connected database)
        str value (what is to be inserted)
        obj cur (database cursor)
        obj con (database connection)

    Return:
        void

    '''
    assert con != None, "No database connection"

    query = f"INSERT INTO {dbTable} ({dbCol}) VALUES (?)"

    val = (value,)

    cur.execute(query,val)

    
    con.commit()