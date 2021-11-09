import pandas as pd
import sqlalchemy
import pymongo
import json
import mysql.connector as connector
from textwrap import wrap
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider


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
            else:
                return f"{file} is not supported!"

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



class cassandra_connector:
    """
    cassandra_connector class performs cassandra database operations,eg: connecting to database,
    creating table, inserting values into table, retriving dataset for allowed filetypes
    """

    def __init__(self, bundel_zip, client_id, client_secret, keyspace):
        try:
            self.cloud_config = {'secure_connect_bundle': bundel_zip}
            self.auth_provider = PlainTextAuthProvider(client_id, client_secret)
            self.cluster = Cluster(cloud=self.cloud_config, auth_provider=self.auth_provider)
            self.keyspace = keyspace
        except Exception as e:
            print(e)

    def connect_to_cluster(self):
        try:
            session = self.cluster.connect(self.keyspace)
            return session
        except Exception as e:
            print(e)

    def push_dataframe_to_table(self, dataframe, table_name):

        try:
            data = dataframe.to_json()
            data = wrap(data, 65000)

            create_query = f'create table {table_name}('
            column_names = []

            for i in range(len(data)):  ## creating create table query and collect column names
                if i == 0:
                    create_query += f'data{i * "1"} text primary key, '
                    column_names.append(f'data{i * "1"}')

                else:
                    create_query += f'data{i * "1"} text ,'
                    column_names.append(f'data{i * "1"}')

            create_query = create_query.strip(" ,") + ");"
            print(create_query)
            session = self.connect_to_cluster()
            session.execute(create_query, timeout=None)

            insert_query = f'insert into {table_name}({", ".join(column_names)}) values ({"? ," * len(column_names)}'.strip(
                ", ") + ");"
            print(insert_query)
            prepared_query = session.prepare(insert_query)
            session.execute(prepared_query, data, timeout=None)
            session.shutdown()
            print("Cassandra session closed")

        except Exception as e:
            print(e)

    def custom_query(self, custom_query):
        try:
            session = self.cluster.connect(self.keyspace)
            data = session.execute(custom_query)
            session.shutdown()
            print("Cassandra session closed")
            return data

        except Exception as e:
            print(e)

    def retrive_table(self, table_name, download_path):
        try:
            session = self.cluster.connect(self.keyspace)
            dataframe = pd.DataFrame(list(session.execute(f"select * from {table_name}")))
            session.shutdown()
            print("Cassandra session closed")
            dataframe.to_csv(download_path, index=False)
            return 'Successful'

        except Exception as e:
            print(e)

    def retrive_uploded_dataset(self, table_name, download_path):
        try:
            session = self.cluster.connect(self.keyspace)
            data = session.execute("select * from neuro")
            dataset_string = ""
            for row in data:
                for chunks in row:
                    dataset_string += chunks
            dataset = json.loads(dataset_string)
            dataframe = pd.DataFrame(dataset)
            dataframe.to_csv(download_path, index=False)
            session.shutdown()
            print("Cassandra session closed")
            return 'Successful'

        except Exception as e:
            print(e)

    def check_connection(self, table_name):
        table_list = []

        try:
            session = self.cluster.connect(self.keyspace)
            query = f"SELECT * FROM system_schema.tables WHERE keyspace_name = '{self.keyspace}';"
            data = session.execute(query)

            for table in data:
                table_list.append(table.table_name)
            if table_name in table_list:
                return "Successful"
            else:
                return f"{table_name} table in not available in '{self.keyspace}' keyspace"

        except Exception as e:

            if 'AuthenticationFailed' in e.__str__():
                return "Given client_id or client_secret is invalid"
            elif 'keyspace' in e.__str__():
                return f"Given {self.keyspace} keyspace does not exist!!"
            else:
                return "Provide valid bundel zip file!!"


class mongo_data_helper():

    def __init__(self, mongo_db_url):
        self.mongo_db_uri = mongo_db_url

    def connect_to_mongo(self):
        client_cloud = pymongo.MongoClient(self.mongo_db_uri)
        return client_cloud

    def close_connection(self, client_cloud):
        client_cloud.close()
        print("Mongo db connection closed")

    def retrive_dataset(self, database_name, collection_name, download_path):

        try:
            client_cloud = self.connect_to_mongo()
            database = client_cloud[database_name]
            collection = database[collection_name]
            dataframe = pd.DataFrame(list(collection.find())).drop(columns='_id')
            dataframe.to_csv(download_path, index=False)
            self.close_connection(client_cloud)
            return "Successful"

        except Exception as e:
            return e.__str__()

    def push_dataset(self, database_name, collection_name, file):

        try:
            if file.endswith('.csv'):
                dataframe = pd.read_csv(file)
            elif file.endswith('.tsv'):
                dataframe = pd.read_csv(file, sep='\t')
            elif file.endswith('.json'):
                dataframe = pd.read_json(file)
            else:
                return "given file is not supported"

            data = dataframe.to_dict('record')

            client_cloud = self.connect_to_mongo()
            database = client_cloud[database_name]
            collection = database[collection_name]
            collection.delete_many({})
            print(f"cleaned {collection_name} collection")
            collection.insert_many(data)

            self.close_connection(client_cloud)
            return 'Successful'

        except Exception as e:
            return e.__str__()

    def check_connection(self, database_name, collection_name):

        try:
            client_cloud = self.connect_to_mongo()
            DBlist = client_cloud.list_database_names()

            if database_name in DBlist:
                database = client_cloud[database_name]
                collection_list = database.list_collection_names()

                if collection_name in collection_list:
                    self.close_connection(client_cloud)
                    return "Successful"
                else:
                    self.close_connection(client_cloud)
                    return f"Given {collection_name} collection does not exits in {database_name} database"
            else:
                self.close_connection(client_cloud)
                return f"Given {database_name} database does not exist!!"

        except Exception as e:
            print(e)
            if "Authentication failed" in e.__str__():
                return "Provide valid Mongo DB URL"
            else:
                return "OOPS something went wrong!!"


