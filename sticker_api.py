import requests
from fastapi import FastAPI
from pydantic import BaseModel
from sticker import StickerProcessor
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get S3 bucket name from environment variables
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
if not S3_BUCKET_NAME:
    raise ValueError("S3_BUCKET_NAME environment variable not set")


class ImageRequest(BaseModel):
    """
    Schema for image URL request.

    **Args:**
        image_url (str): URL of the image to process.

    **Returns:**
        ImageRequest: An instance of ImageRequest with the provided image URL.
    """
    image_url: str


class StickerAPI:
    """
    FastAPI application for generating stickers and removing backgrounds from images.

    **Args:**
        s3_bucket_name (str): Name of the S3 bucket for storing and retrieving images.

    **Returns:**
        StickerAPI: An instance of the FastAPI application with configured routes.
    """

    def __init__(self, s3_bucket_name: str):
        """
        Initialize the StickerAPI instance.

        **Args:**
            s3_bucket_name (str): Name of the S3 bucket for storing and retrieving images.

        **Returns:**
            None
        """
        self.s3_bucket_name = s3_bucket_name
        self.processor = StickerProcessor(
            yolo_model_path="yolov8n.pt",
            sam_checkpoint_path="sam_vit_h_4b8939.pth",
            sam_model_type="vit_h",
            s3_bucket_name=self.s3_bucket_name
        )
        self.app = FastAPI(title="BG Remove & Sticker Generation API")
        self.setup_routes()

        # Allow all origins (CORS)
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    def setup_routes(self):
        """
        Define the routes for the FastAPI app.

        **Returns:**
            None
        """
        self.app.post("/generate-sticker/")(self.generate_sticker_api)
        self.app.post("/remove-background/")(self.remove_background_api)

    def is_valid_url(self, url: str) -> bool:
        """
        Check the validity of a URL by sending a HEAD request.

        **Args:**
            url (str): The URL to be checked.

        **Returns:**
            bool: True if the URL is reachable, False otherwise.
        """
        try:
            response = requests.head(url, timeout=5)
            return response.status_code == 200
        except Exception:
            return False

    async def generate_sticker_api(self, image_request: ImageRequest):
        """
        API endpoint to generate a sticker with the given image URL.

        **Args:**
            image_request (ImageRequest): Request body containing the image URL.

        **Returns:**
            dict: A dictionary with the status and either the sticker URL or error details.

                - If successful, returns {"status": 1, "detail": {"sticker_url": sticker_url}}

                - If the URL is invalid or inaccessible, returns {"status": 0, "detail": {"error_type": "InvalidURL", "details": "The provided image URL is not reachable or invalid."}}

                - If there is an error during processing, returns {"status": 0, "detail": result}

                - For unexpected exceptions, returns {"status": 0, "detail": {"error_type": "StickerGenerationError", "details": "<Exception message>"}}
        """
        # Validate the image URL first
        if not self.is_valid_url(image_request.image_url):
            return {
                "status": 0,
                "detail": {
                    "error_type": "invalid_url",
                    "details": "The provided image URL is not reachable or invalid."
                }
            }

        # If URL is valid, proceed to generate sticker
        result = self.processor.generate_sticker(image_request.image_url)

        # If there's an error during processing, return it
        if isinstance(result, dict) and "error_type" in result:
            return {
                "status": 0,
                "detail": result
            }

        return {
            "status": 1,
            "detail": {
                "sticker_url": result["sticker_url"]
            }
        }

    async def remove_background_api(self, image_request: ImageRequest):
        """
        API endpoint to remove the background from the image with the given image URL.

        **Args:**
            image_request (ImageRequest): Request body containing the image URL.

        **Returns:**
            dict: A dictionary with the status and either the background-removed URL or error details.

                - If successful, returns {"status": 1, "detail": {"bg_removed_url": bg_removed_url}}

                - If the URL is invalid or inaccessible, returns {"status": 0, "detail": {"error_type": "InvalidURL", "details": "The provided image URL is not reachable or invalid."}}

                - If there is an error during processing, returns {"status": 0, "detail": result}

                - For unexpected exceptions, returns {"status": 0, "detail": {"error_type": "BackgroundRemovalError", "details": "<Exception message>"}}
        """
        # Validate the image URL first
        if not self.is_valid_url(image_request.image_url):
            return {
                "status": 0,
                "detail": {
                    "error_type": "invalid_url",
                    "details": "The provided image URL is not reachable or invalid."
                }
            }

        # If URL is valid, proceed to remove background
        result = self.processor.remove_background(image_request.image_url)

        # If there's an error during processing, return it
        if isinstance(result, dict) and "error_type" in result:
            return {
                "status": 0,
                "detail": result
            }

        return {
            "status": 1,
            "detail": {
                "bg_removed_url": result["bg_removed_url"]
            }
        }


# Instantiate StickerAPI
sticker_api = StickerAPI(S3_BUCKET_NAME)

# FastAPI app instance
app = sticker_api.app
