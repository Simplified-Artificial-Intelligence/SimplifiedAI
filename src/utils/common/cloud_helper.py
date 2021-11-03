import boto3
import pandas as pd


class aws_s3_helper():

    def __init__(self, region_name, aws_access_key_id, aws_secret_access_key):
        self.region_name = region_name
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key
        self.s3 = boto3.resource(service_name='s3',
                                 region_name=self.region_name,
                                 aws_access_key_id=self.aws_access_key_id,
                                 aws_secret_access_key=self.aws_secret_access_key)

    def check_available_buckets(self):
        bucket_list = []
        try:
            for bucket in self.s3.buckets.all():
                bucket_list.append(bucket.name)
        except Exception as e:
            return False
        return bucket_list

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
        except Exception as e:
            return e
        return f"{file} downloded successfully to {download_filepath}"
