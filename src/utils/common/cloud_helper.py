import boto3
import pandas as pd
from google.cloud import storage



class aws_s3_helper():

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
            return False

    def show_files_in_bucket(self, bucket_name):
        file_list = []
        try:
            for obj in self.s3.Bucket(bucket_name).objects.all():
                file_list.append(obj.key)
            return file_list
        except Exception as e:
            return False

    def push_file_to_s3(self, bucket, file):
        try:
            self.s3.Bucket(bucket).upload_file(Filename=file, Key=file)
        except Exception as e:
            return e
        return f"{file} uploded successfully to {bucket}"

    def read_file_from_s3(self, bucket, file):

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
        return dataframe

    def download_file_from_s3(self, bucket, file, download_filepath):
        try:
            self.s3.Bucket(bucket).download_file(Filename=download_filepath, Key=file)
            print(f"{file} downloded successfully to {download_filepath}")
            return 'Successful'

        except Exception as e:
            return e.__str__()



class gcp_browser_storage():
    def __init__(self, credentials_file):
        try:
            self.storage_client = storage.Client.from_service_account_json(credentials_file)
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
            return "f{bucket_name} created!"

        except Exception as e:
            print(e)
            return "f{bucket_name} was not created!"

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
        '''
            Upload file to a bucket
            : blob_name  (str) - object name
            : file_path (str)
            : bucket_name (str)
        '''
        try:
            bucket = self.storage_client.get_bucket(bucket_name)
            blob = bucket.blob(blob_name)
            blob.upload_from_filename(file_path)
            print("{blob_name} was uploded to {bucket_name}")
            return blob

        except Exception as e:
            print("{blob_name} was not uploded to {bucket_name}")
            print(e)

    def download_file_from_bucket(self, blob_name, file_path, bucket_name):

        '''
            download file from bucket
            : blob_name  (str) - object name
            : file_path (str)
            : bucket_name (str)
        '''

        try:
            bucket = storage_client.get_bucket(bucket_name)
            blob = bucket.blob(blob_name)
            with open(file_path, 'wb') as f:
                storage_client.download_blob_to_file(blob, f)
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
            return 'Provide valid credentials json file provided by gcp after creating key in gcp service account'


