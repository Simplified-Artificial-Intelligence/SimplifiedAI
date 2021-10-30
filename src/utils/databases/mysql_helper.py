import mysql.connector as connector
import mysql.connector.pooling

"""
    [summary]
        Mysql Helper for all operations related to mysql
    Returns:
        [type]: [None]
"""


class MySqlHelper:
    def __init__(self, host, port, user, password, database):
        """
        [summary]: Constructor
        Args:
            host ([type]): [description]
            port ([type]): [description]
            user ([type]): [description]
            password ([type]): [description]
            database ([type]): [description]
        """
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database
        self.isconnected=False
        
        dbconfig = {
            "host":host,
            "port":port,
            "user":user,
            "password":password,
            "database":database,
        }
        self.pool = self.create_pool(dbconfig,"auto_neuron_pool", 3)
        # self.connect_todb()

    def connect_todb(self):
            self.connection = connector.connect(host=self.host, port=self.port, user=self.user,
                                    password=self.password, database=self.database, use_pure=True)
            self.isconnected=True

    def create_pool(self,dbconfig, pool_name="mypool", pool_size=3):
        """[summary]
                Create a connection pool, after created, the request of connecting 
                MySQL could get a connection from this pool instead of request to 
                create a connection.
        Args:
            pool_name (str, optional): [description]. Defaults to "mypool".
            pool_size (int, optional): [description]. Defaults to 3.

        Returns:
            [type]: [description]
        """
        pool = mysql.connector.pooling.MySQLConnectionPool(
            pool_name=pool_name,
            pool_size=pool_size,
            pool_reset_session=True,
            **dbconfig)
        return pool
    
    
    def close(self, conn, cursor):
        """
        A method used to close connection of mysql.
        :param conn: 
        :param cursor: 
        :return: 
        """
        cursor.close()
        # conn.close()
        
    def fetch_all(self, query):
        """
        [summary]: This function will return all record from table
        Args:
            query ([type]): [Select tabel query]

        Returns:
            [type]: [description]
        """
        try:
            conn = self.pool.get_connection()
            cursor = conn.cursor()
            
            cursor.execute(query)
            data = cursor.fetchall()
            return data

        except connector.Error as error:
            print("Error: {}".format(error))

        finally:
                self.close(conn, cursor)
                print("MySQL connection is closed")

    def fetch_one(self, query):
        """
        [summary]:This method return single record from table
        Args:
            query ([type]): [Query to execute]

        Returns:
            [type]: [Data]
        """
        try:
            conn = self.pool.get_connection()
            cursor = conn.cursor()
            cursor.execute(query)
            data = cursor.fetchone()
            return data

        except connector.Error as error:
            print("Error: {}".format(error))

        finally:
            cursor.commit()
            self.close(conn, cursor)
            print("MySQL connection is closed")

    def delete_record(self, query):
        """
        [summary]: Function to delete record from table single or multiple
        Args:
            query ([type]): [Query to execute]

        Returns:
            [type]: [No of row effected]
        """
        try:
            conn = self.pool.get_connection()
            cursor = conn.cursor()
            cursor.execute(query)
            rowcount = cursor.rowcount
            return rowcount

        except connector.Error as error:
            print("Error: {}".format(error))

        finally:
            conn.commit()
            self.close(conn, cursor)
            print("MySQL connection is closed")


    def insert_record(self, query):
        """
        [summary]:Insert record into table
        Args:
            query ([type]): [Query to execute]

        Returns:
            [type]: [1 if row inserted or 0 if not]
        """
        try:
            conn = self.pool.get_connection()
            cursor = conn.cursor()
            cursor.execute(query)
            rowcount = cursor.rowcount
            cursor.close()
            return rowcount

        except connector.Error as error:
            print("Error: {}".format(error))

        finally:
            conn.commit()
            # self.close(conn, cursor)
