import boto3
import gzip
import json
import os
import shutil


class Outfile(object):
    def __init__(self, file_path):
        self.file_path = file_path
        self.compressed_file_path = "%s.gz" % file_path
        self.s3_key = os.path.basename(self.compressed_file_path)

    def flush(self, json_list):
        with open(self.file_path, 'w') as out_file:
            for item in json_list:
                out_file.write(json.dumps(item) + '\n')

    def compress(self):
        in_name = self.file_path
        out_name = self.compressed_file_path
        with open(in_name, 'rb') as f_in, gzip.open(out_name, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)
        os.remove(in_name)

    def upload_to_s3(self, bucket_name):
        s3 = boto3.client('s3')
        upload_message = "Uploading %s to S3 bucket %s" % (self.s3_key,
                                                           bucket_name)
        print(upload_message)
        s3.upload_file(self.compressed_file_path, bucket_name, self.s3_key)
