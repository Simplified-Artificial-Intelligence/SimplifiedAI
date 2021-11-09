import boto3
import pandas as pd
from google.cloud import storage
from azure.storage.blob import BlobClient
from azure.storage.blob import ContainerClient
from azure.storage.blob import BlobServiceClient


class aws_s3_helper:
    def __init__(self, region_name, aws_access_key_id, aws_secret_access_key):
        self.region_name = region_name
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key
        self.s3 = boto3.resource(service_name='s3',
                                 region_name=self.region_name,
                                 aws_access_key_id=self.aws_access_key_id,
                                 aws_secret_access_key=self.aws_secret_access_key)

    def check_connection(self, bucket_name, file_name):
        bucket_list = []
        file_list = []
        try:
            for bucket in self.s3.buckets.all():
                bucket_list.append(bucket.name)
            if bucket_name in bucket_list:
                for obj in self.s3.Bucket(bucket_name).objects.all():
                    file_list.append(obj.key)
                if file_name in file_list:
                    return "Successful"
                else:
                    return "File does not exist!!"
            else:
                return "Bucket does not exist!!"

        except Exception as e:

            if 'InvalidAccessKeyId' in e.__str__():
                return 'aws access key id is not valid!!'
            elif 'SignatureDoesNotMatch' in e.__str__():
                return 'aws secret access key is not valid!!'
            elif 'endpoint' in e.__str__():
                return 'Given region is not valid!!'
            elif 'Not Found' in e.__str__():
                return 'Given bucket or file is not valid'
            else:
                return 'oops something went wrong!!'

    def check_available_buckets(self):
        bucket_list = []
        try:
            for bucket in self.s3.buckets.all():
                bucket_list.append(bucket.name)
            return bucket_list

        except Exception as e:
            print(e)
            return False

    def show_files_in_bucket(self, bucket_name):
        file_list = []
        try:
            for obj in self.s3.Bucket(bucket_name).objects.all():
                file_list.append(obj.key)
            return file_list
        except Exception as e:
            print(e)
            return False

    def push_file_to_s3(self, bucket, file):
        try:
            self.s3.Bucket(bucket).upload_file(Filename=file, Key=file)
        except Exception as e:
            return e
        return f"{file} uploaded successfully to {bucket}"

    def read_file_from_s3(self, bucket, file):
        dataframe = None
        if file.endswith('.csv'):
            obj = self.s3.Bucket(bucket).Object(file).get()
            dataframe = pd.read_csv(obj['Body'], index_col=0)
            print(obj)
        elif file.endswith('.tsv'):
            obj = self.s3.Bucket(bucket).Object(file).get()
            dataframe = pd.read_tsv(obj['Body'], index_col=0)
        elif file.endswith('.json'):
            obj = self.s3.Bucket(bucket).Object(file).get()
            dataframe = pd.read_json(obj['Body'], index_col=0)
        else:
            pass
        return dataframe

    def download_file_from_s3(self, bucket, file, download_filepath):
        try:
            self.s3.Bucket(bucket).download_file(Filename=download_filepath, Key=file)
            print(f"{file} downloaded successfully to {download_filepath}")
            return 'Successful'

        except Exception as e:
            return e.__str__()


class gcp_browser_storage:
    def __init__(self, credentials_file):
        try:
            self.storage_client = storage.Client.from_service_account_json(credentials_file)
            print('done')
        except Exception as e:
            print(e.__str__())
            # return 'Provide proper credentials file in json'

    # create a new bucket
    def create_bucket(self, bucket_name, project, storage_class, location):
        try:
            bucket = self.storage_client.bucket(bucket_name)
            bucket.storage_class = storage_class  # Archive | Nearline | Standard | Coldline
            bucket.location = location  # Taiwan
            bucket = self.storage_client.create_bucket(bucket)  # returns Bucket object
            return f"{bucket_name} created!"

        except Exception as e:
            print(e)
            return f"{bucket_name} was not created!"

    def list_buckets(self):
        bucket_list = []
        try:
            for bucket in self.storage_client.list_buckets():
                bucket_list.append(bucket.name)
            return bucket_list

        except Exception as e:
            print(e)

    def list_file_in_buckets(self, bucket_name):
        file_list = []
        try:
            for file in self.storage_client.list_blobs(bucket_name):
                file_list.append(file.name)
            return file_list

        except Exception as e:
            print(e)

    def upload_to_bucket(self, blob_name, file_path, bucket_name):
        """
            Upload file to a bucket
            : blob_name  (str) - object name
            : file_path (str)
            : bucket_name (str)
        """
        try:
            bucket = self.storage_client.get_bucket(bucket_name)
            blob = bucket.blob(blob_name)
            blob.upload_from_filename(file_path)
            print("{blob_name} was uploaded to {bucket_name}")
            return blob

        except Exception as e:
            print("{blob_name} was not uploaded to {bucket_name}")
            print(e)

    def download_file_from_bucket(self, blob_name, file_path, bucket_name):

        """
            download file from bucket
            : blob_name  (str) - object name
            : file_path (str)
            : bucket_name (str)
        """

        try:
            bucket = self.storage_client.get_bucket(bucket_name)
            blob = bucket.blob(blob_name)
            with open(file_path, 'wb') as f:
                self.storage_client.download_blob_to_file(blob, f)
            print('Saved')
            return 'Successful'

        except Exception as e:
            print(e)

    def check_connection(self, bucket_name, file_name):
        bucket_list = []
        file_list = []

        try:
            for bucket in self.storage_client.list_buckets():
                bucket_list.append(bucket.name)
            if bucket_name in bucket_list:
                for file in self.storage_client.list_blobs(bucket_name):
                    file_list.append(file.name)
                if file_name in file_list:
                    return 'Successful'
                else:
                    return f'The {file_name} does not exist {bucket_name} bucket!!'
            else:
                return f'The {bucket_name} bucket does not exist!!'

        except Exception as e:
            print(e)
            return 'Provide valid credentials json file provided by gcp during the creation of gcp service account'


class azure_data_helper():
    def __init__(self, connection_string):
        try:
            self.connection_string = connection_string
            self.blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)
        except Exception as e:
            print(e)

    def create_container(self, container_name):
        try:
            self.blob_service_client.create_container(container_name)
            print(f"{container_name} container created!!")
            return 'Successful'

        except Exception as e:
            print(e.__str__())
            if 'Server failed to authenticate' or 'blank or malformed' in e.__str__():
                return 'Provide valid azure connection string'
            else:
                return 'OOPS something went wrong!!'

    def delete_container(self, container_name):
        try:
            self.blob_service_client.delete_container(container_name)
            print(f"{container_name} container deleted!!")
            return 'Successful'

        except Exception as e:
            print(e.__str__())
            if 'Server failed to authenticate' or 'blank or malformed' in e.__str__():
                return 'Provide valid azure connection string'
            else:
                return 'OOPS something went wrong!!'

    def upload_file(self, file_path, container_name):
        try:
            blob = BlobClient.from_connection_string(conn_str=self.connection_string, container_name=container_name,
                                                     blob_name=file)
            with open(file, "rb") as data:
                blob.upload_blob(data)
            print(f"{file} is uploded to {container_name} container")
            return 'Successful'

        except Exception as e:
            print(e.__str__())
            if 'Server failed to authenticate' or 'blank or malformed' in e.__str__():
                return 'Provide valid azure connection string'
            else:
                return 'OOPS something went wrong!!'

    def download_file(self, container_name, file_name, download_file_path):
        try:
            blob = BlobClient.from_connection_string(conn_str=self.connection_string, container_name=container_name,
                                                     blob_name=file_name)
            with open(download_file_path, "wb") as my_blob:
                blob_data = blob.download_blob()
                blob_data.readinto(my_blob)
            print(f"{file_name} downloded from {container_name} container to {download_file_path}")
            return 'Successful'

        except Exception as e:
            print(e.__str__())
            if 'Server failed to authenticate' or 'blank or malformed' in e.__str__():
                return 'Provide valid azure connection string'
            else:
                return 'OOPS something went wrong!!'

    def list_containers(self):
        container_list = []
        try:
            for container in self.blob_service_client.list_containers():
                container_list.append(container.name)
            return container_list

        except Exception as e:
            # print(e.__str__())
            if 'Server failed to authenticate' or 'blank or malformed' in e.__str__():
                return 'Provide valid azure connection string'
            else:
                return 'OOPS something went wrong!!'

    def list_blobs(self, container_name):
        my_blob_list = []
        try:
            container = ContainerClient.from_connection_string(conn_str=self.connection_string,
                                                               container_name=container_name)
            blob_list = container.list_blobs()
            for blob in blob_list:
                my_blob_list.append(blob.name)
            return my_blob_list

        except Exception as e:
            print(e.__str__())
            if 'Server failed to authenticate' or 'blank or malformed' in e.__str__():
                return 'Provide valid azure connection string'
            else:
                return 'OOPS something went wrong!!'

    def check_connection(self, container_name, file_name):
        try:
            containers = self.list_containers()

            if type(containers) != list:
                return containers
            elif container_name in containers:
                blobs = self.list_blobs(container_name)
                if file_name in blobs:
                    return 'Successful'
                else:
                    return f"{file_name} does not exist in {container_name} container!!"
            else:
                return f"{container_name} container does not exist!!"

        except Exception as e:
            print(e.__str__())
            if 'Server failed to authenticate' or 'blank or malformed' in e.__str__():
                return 'Provide valid azure connection string'
            else:
                return 'OOPS something went wrong!!'


