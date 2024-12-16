# import os
# import boto3
# from dotenv import load_dotenv
# import requests
# from urllib.parse import urlparse, unquote
# import re

# # Load environment variables from .env file
# load_dotenv()

# class StickerManager:
#     @staticmethod
#     def get_timestamp():
#         """
#         Return the current timestamp as a string.

#         :returns: A string representing the current timestamp in the format 'YYYYMMDD_HHMMSS'.
#         :rtype: str
#         """
#         from datetime import datetime
#         return datetime.now().strftime('%Y%m%d_%H%M%S')
    


#     @staticmethod
#     def download_image(image_url, download_folder):
#         """
#         Download an image from a given URL and save it to a specified folder.

#         :param image_url: URL of the image to be downloaded.
#         :type image_url: str
#         :param download_folder: Folder where the downloaded image will be saved.
#         :type download_folder: str
#         :returns: Path to the downloaded image file or a dictionary with error details.
#         :rtype: str or dict
#         :raises ValueError: If the URL does not point to a valid image or if downloading fails.
#         """
#         try:
#             os.makedirs(download_folder, exist_ok=True)
#             parsed_url = urlparse(image_url)
#             image_name = os.path.basename(parsed_url.path)
#             image_name = unquote(image_name.split('?')[0])

#             # Validate if the URL has an image file extension
#             if not re.search(r'\.(bmp|jpeg|jpg|png|tiff|webp)$', image_name, re.IGNORECASE):
#                 image_name += ".jpg"

#             # Add timestamp to the image name
#             timestamp = StickerManager.get_timestamp()
#             image_name = f"{timestamp}_{image_name}"
#             image_path = os.path.join(download_folder, image_name)

#             # Download image
#             response = requests.get(image_url, timeout=5)
#             print(f"Fetching URL: {image_url}, Status Code: {response.status_code}")

#             if response.status_code == 200:
#                 with open(image_path, 'wb') as f:
#                     f.write(response.content)
#             else:
#                 raise Exception(f"Failed to download image from URL: {image_url}. HTTP Status Code: {response.status_code}")

#             return image_path
#         except requests.exceptions.RequestException as e:
#             return {"error_type": "Download_Error", "details": str(e)}
#         except Exception as e:
#             return {"error_type": "Download_Error", "details": str(e)}

#     @staticmethod
#     def upload_to_s3(file_path, s3_bucket, s3_key, content_type='image/png'):
#         """
#         Upload a file to an S3 bucket.

#         :param file_path: Path to the local file to be uploaded.
#         :type file_path: str
#         :param s3_bucket: Name of the S3 bucket.
#         :type s3_bucket: str
#         :param s3_key: Key (path) for the file in the S3 bucket.
#         :type s3_key: str
#         :param content_type: MIME type of the file, defaults to 'image/png'.
#         :type content_type: str, optional
#         :returns: None or a dictionary with error details.
#         :rtype: None or dict
#         :raises FileNotFoundError: If the file does not exist.
#         """
#         try:
#             s3_client = boto3.client(
#                 's3',
#                 aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
#                 aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
#                 region_name=os.getenv('AWS_REGION')
#             )

#             if not os.path.exists(file_path):
#                 raise FileNotFoundError(f"File {file_path} does not exist")

#             s3_client.upload_file(
#                 file_path, 
#                 s3_bucket, 
#                 s3_key, 
#                 ExtraArgs={'ContentType': content_type, 'ACL': 'public-read'}
#             )
#         except Exception as e:
#             return {"error_type": "S3_Upload_Error", "details": str(e)}

#     @staticmethod
#     def generate_presigned_url(s3_bucket, s3_key):
#         """
#         Generate a presigned URL for accessing an object in S3.

#         :param s3_bucket: Name of the S3 bucket.
#         :type s3_bucket: str
#         :param s3_key: Key (path) for the file in the S3 bucket.
#         :type s3_key: str
#         :returns: Presigned URL for the S3 object or a dictionary with error details.
#         :rtype: str or dict
#         """
#         try:
#             s3_client = boto3.client(
#                 's3',
#                 aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
#                 aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
#                 region_name=os.getenv('AWS_REGION')
#             )
#             response = s3_client.generate_presigned_url('get_object',
#                                                         Params={'Bucket': s3_bucket, 'Key': s3_key})
#             return response
#         except Exception as e:
#             return {"error_type": "URL_Generation_Error", "details": str(e)}

#     @staticmethod
#     def clean_local_files(*file_paths):
#         """
#         Remove specified local files.

#         :param file_paths: Paths to the files to be removed.
#         :type file_paths: str
#         :returns: None or a dictionary with error details.
#         :rtype: None or dict
#         """
#         try:
#             for file_path in file_paths:
#                 if os.path.exists(file_path):
#                     os.remove(file_path)
#         except Exception as e:
#             print({"error_type": "Cleanup_Error", "details": str(e)})






import os
import boto3
from dotenv import load_dotenv
import requests
from urllib.parse import urlparse, unquote
import re

# Load environment variables from .env file
load_dotenv()

class StickerManager:
    @staticmethod
    def get_timestamp():
        """
        Return the current timestamp as a string.

        :returns: A string representing the current timestamp in the format 'YYYYMMDD_HHMMSS'.
        :rtype: str
        """
        from datetime import datetime
        return datetime.now().strftime('%Y%m%d_%H%M%S')

    @staticmethod
    def download_image(image_url, download_folder):
        """
        Download an image from a given URL and save it to a specified folder.

        :param image_url: URL of the image to be downloaded.
        :type image_url: str
        :param download_folder: Folder where the downloaded image will be saved.
        :type download_folder: str
        :returns: Path to the downloaded image file or a dictionary with error details.
        :rtype: str or dict
        :raises ValueError: If the URL does not point to a valid image or if downloading fails.
        """
        try:
            os.makedirs(download_folder, exist_ok=True)
            parsed_url = urlparse(image_url)
            image_name = os.path.basename(parsed_url.path)
            image_name = unquote(image_name.split('?')[0])

            # Validate if the URL has an image file extension
            if not re.search(r'\.(bmp|jpeg|jpg|png|tiff|webp)$', image_name, re.IGNORECASE):
                image_name += ".jpg"

            # Add timestamp to the image name
            timestamp = StickerManager.get_timestamp()
            image_name = f"{timestamp}_{image_name}"
            image_path = os.path.join(download_folder, image_name)

            # Download image
            response = requests.get(image_url, timeout=5)
            print(f"Fetching URL: {image_url}, Status Code: {response.status_code}")

            if response.status_code == 200:
                with open(image_path, 'wb') as f:
                    f.write(response.content)
            else:
                raise Exception(f"Failed to download image from URL: {image_url}. HTTP Status Code: {response.status_code}")

            return image_path
        except requests.exceptions.RequestException as e:
            return {"error_type": "Download_Error", "details": str(e)}
        except Exception as e:
            return {"error_type": "Download_Error", "details": str(e)}

    @staticmethod
    def upload_to_s3(file_path, s3_bucket, s3_key, content_type='image/png'):
        """
        Upload a file to an S3 bucket.

        :param file_path: Path to the local file to be uploaded.
        :type file_path: str
        :param s3_bucket: Name of the S3 bucket.
        :type s3_bucket: str
        :param s3_key: Key (path) for the file in the S3 bucket.
        :type s3_key: str
        :param content_type: MIME type of the file, defaults to 'image/png'.
        :type content_type: str, optional
        :returns: None or a dictionary with error details.
        :rtype: None or dict
        :raises FileNotFoundError: If the file does not exist.
        """
        try:
            s3_client = boto3.client(
                's3',
                aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
                region_name=os.getenv('AWS_REGION')
            )

            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File {file_path} does not exist")

            s3_client.upload_file(
                file_path, 
                s3_bucket, 
                s3_key, 
                ExtraArgs={'ContentType': content_type, 'ACL': 'public-read'}
            )
        except Exception as e:
            return {"error_type": "S3_Upload_Error", "details": str(e)}

    @staticmethod
    def generate_presigned_url(s3_bucket, s3_key):
        """
        Generate a presigned URL for accessing an object in S3.

        :param s3_bucket: Name of the S3 bucket.
        :type s3_bucket: str
        :param s3_key: Key (path) for the file in the S3 bucket.
        :type s3_key: str
        :returns: Presigned URL for the S3 object or a dictionary with error details.
        :rtype: str or dict
        """
        try:
            s3_client = boto3.client(
                's3',
                aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
                region_name=os.getenv('AWS_REGION')
            )
            response = s3_client.generate_presigned_url('get_object',
                                                        Params={'Bucket': s3_bucket, 'Key': s3_key})
            return response
        except Exception as e:
            return {"error_type": "URL_Generation_Error", "details": str(e)}

    @staticmethod
    def clean_local_files(*file_paths):
        """
        Remove specified local files.

        :param file_paths: Paths to the files to be removed.
        :type file_paths: str
        :returns: None or a dictionary with error details.
        :rtype: None or dict
        """
        try:
            for file_path in file_paths:
                if os.path.exists(file_path):
                    os.remove(file_path)
            print("Local files cleaned up successfully.")
        except Exception as e:
            print({"error_type": "Cleanup_Error", "details": str(e)})
