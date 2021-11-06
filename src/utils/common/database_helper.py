import pandas as pd
import sqlalchemy
import mysql.connector as connector


class mysql_data_helper():
    def __init__(self, host, port, user, password, database):
        # def __init__(self, host, user, password, database):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database  # dialect+driver://username:password@host:port/database.
        self.engine = sqlalchemy.create_engine(f"""mysql+mysqlconnector://{self.user}:{self.password}@
                                                   {self.host}:{self.port}/{self.database}""")

    def connect_todb(self):  #
        self.connection = self.engine.connect()
        return self.connection

    def custom_query(self, query):
        conn = self.connect_todb()
        results = conn.execute(query).fetchall()
        return results

    def retrive_dataset_from_table(self, table_name, download_path):
        try:
            conn = self.connect_todb()
            data_query = f"select * from {table_name}"
            schema_query = f"describe {table_name}"
            data = conn.execute(data_query).fetchall()
            schema = conn.execute(schema_query).fetchall()
            conn.close()

            column_names = []
            for row in schema:
                column_names.append(row[0])
            try:
                dataframe = pd.DataFrame(data, columns=column_names).drop(columns='index')
                dataframe.to_csv(download_path, index=False)
                return 'Successful'
            except Exception as e:
                print(e)
                dataframe = pd.DataFrame(data, columns=column_names)
                dataframe.to_csv(download_path, index=False)
                return 'Successful'

        except Exception as e:
            return e.__str__()

    def push_file_to_table(self, file, table_name):
        try:
            if file.endswith(".csv"):
                dataframe = pd.read_csv(file)
            elif file.endswith(".tsv"):
                dataframe = pd.read_csv(file, sep="\t")
            elif file.endswith(".json"):
                dataframe = pd.read_json(file)
            try:
                dataframe.to_sql(con=self.engine, name=table_name, if_exists='replace', chunksize=1000)
                return f"{file} was pushed into {table_name} table!"

            except Exception as e:
                return f"could'nt push {file} into {table_name} table!"

        except Exception as e:
            print(e)

    def check_connection(self, table_name):

        table_list = []
        try:
            conn = self.connect_todb()
            query = 'SHOW TABLES'
            data = conn.execute(query).fetchall()
            conn.close()
            for i in data:
                for table in i:
                    table_list.append(table)
            if table_name in table_list:
                return "Successful"
            else:
                return f"{table_name} table does not exist in {self.database} database"

        except Exception as e:

            if 'Unknown database' in e.__str__():
                return f"{self.database} database not found!!"
            elif 'Access denied' in e.__str__():
                return "Incorrect Mysql User or Password!!"
            elif "Can't connect" in e.__str__():
                return "Incorrect Host Given"
            else:
                return "OOPS something went wrong!!"

    def __str__(self):
        return "mysql dataset helper"
