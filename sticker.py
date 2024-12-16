# import os
# import numpy as np
# import cv2
# from ultralytics import YOLO
# from segment_anything import sam_model_registry, SamPredictor
# from PIL import Image
# from sticker_file_operation import StickerManager

# class StickerProcessor:
#     """
#     A class to handle sticker processing including object detection, background removal,
#     and sticker generation using YOLO and SAM models.

#     :param yolo_model_path: Path to the YOLO model file.
#     :type yolo_model_path: str
#     :param sam_checkpoint_path: Path to the SAM model checkpoint file.
#     :type sam_checkpoint_path: str
#     :param sam_model_type: Type of the SAM model to use.
#     :type sam_model_type: str
#     :param s3_bucket_name: Name of the S3 bucket for storing and retrieving images.
#     :type s3_bucket_name: str
#     """

#     def __init__(self, yolo_model_path, sam_checkpoint_path, sam_model_type, s3_bucket_name):
#         """
#         Initialize the StickerProcessor with the paths to the models and the S3 bucket name.

#         :param yolo_model_path: Path to the YOLO model file.
#         :type yolo_model_path: str
#         :param sam_checkpoint_path: Path to the SAM model checkpoint file.
#         :type sam_checkpoint_path: str
#         :param sam_model_type: Type of the SAM model to use.
#         :type sam_model_type: str
#         :param s3_bucket_name: Name of the S3 bucket for storing and retrieving images.
#         :type s3_bucket_name: str
#         """
#         print("Initializing StickerProcessor...")
#         self.yolo_model_path = yolo_model_path
#         self.sam_checkpoint_path = sam_checkpoint_path
#         self.sam_model_type = sam_model_type
#         self.s3_bucket_name = s3_bucket_name

#         # Load YOLO model
#         self.model = YOLO(yolo_model_path)

#         # Load SAM model
#         sam = sam_model_registry[sam_model_type](checkpoint=sam_checkpoint_path)
#         self.predictor = SamPredictor(sam)

#         # Define root directory for saving images and stickers
#         self.root_dir = os.path.dirname(os.path.abspath(__file__))
#         self.img_folder = os.path.join(self.root_dir, "img")
#         self.sticker_folder = os.path.join(self.root_dir, "sticker")
#         self.bg_removed_folder = os.path.join(self.root_dir, "bg_removed")

#         # os.makedirs(self.img_folder, exist_ok=True)
#         # os.makedirs(self.sticker_folder, exist_ok=True)
#         # os.makedirs(self.bg_removed_folder, exist_ok=True)
#             # Debugging paths
#         print(f"Root directory: {self.root_dir}")
#         print(f"Image folder path: {self.img_folder}")
#         print(f"Sticker folder path: {self.sticker_folder}")
#         print(f"Background removed folder path: {self.bg_removed_folder}")

#         try:
#             os.makedirs(self.img_folder, exist_ok=True)
#             os.makedirs(self.sticker_folder, exist_ok=True)
#             os.makedirs(self.bg_removed_folder, exist_ok=True)
#             print("Directories created successfully.")
#         except Exception as e:
#             print(f"Error creating directories: {str(e)}")

#     def predict(self, image_path):
#         """
#         Predict the bounding box of objects in the given image using YOLO.

#         :param image_path: Path to the image file.
#         :type image_path: str
#         :returns: List of bounding boxes for detected objects or an error dictionary.
#         :rtype: list or dict
#         """
#         try:
#             results = self.model.predict(image_path, save=False, verbose=False)
#             if not results:
#                 raise Exception(f"No prediction result from the model for {image_path}")

#             for result in results:
#                 boxes = result.boxes
#             bbox = boxes.xyxy.tolist()[0]
#             return bbox
#         except Exception as e:
#             return {"error_type": "Prediction Error", "details": str(e)}

#     def process_img(self, image_path, bbox, output_path_segmented, border_thickness=10):
#         """
#         Process the image to create a sticker by applying the mask to the image.

#         :param image_path: Path to the input image file.
#         :type image_path: str
#         :param bbox: Bounding box coordinates for the object.
#         :type bbox: list
#         :param output_path_segmented: Path to save the output sticker image.
#         :type output_path_segmented: str
#         :returns: None if successful, otherwise an error dictionary.
#         :rtype: None or dict
#         """
#         try:
#             image = cv2.cvtColor(cv2.imread(image_path), cv2.COLOR_BGR2RGB)
#             self.predictor.set_image(image)
#             input_box = np.array(bbox)
#             masks, _, _ = self.predictor.predict(box=input_box[None, :], multimask_output=False)
#             mask = masks[0]
#             # Convert mask to binary format
#             binary_mask = (mask > 0.5).astype(np.uint8)
#             rgba_image = cv2.cvtColor(image, cv2.COLOR_RGB2RGBA)
#             rgba_image[:, :, 3] = (mask * 255).astype(np.uint8)

#             # Dilate the mask to create a border around the object
#             kernel = np.ones((border_thickness, border_thickness), np.uint8)
#             dilated_mask = cv2.dilate(binary_mask, kernel, iterations=1)
            
#             # Create the border by subtracting the original mask from the dilated mask
#             border_mask = dilated_mask - binary_mask

#             # Apply white border where the border_mask is set
#             rgba_image[border_mask == 1] = [255, 255, 255, 255]  # White color with full opacity

#             pil_image = Image.fromarray(rgba_image)
#             pil_image.save(output_path_segmented)
#             return None  # Return None if successful
#         except Exception as e:
#             return {"error_type": "Sticker Generation Error", "details": str(e)}

#     def remove_background_and_save(self, image_path, bbox, output_path_background_removed, edge_smooth_radius=2, dilation_kernel_size=10):
#         """
#         Remove the background from the image, apply edge smoothing, and save the result.

#         :param image_path: Path to the input image file.
#         :type image_path: str
#         :param bbox: Bounding box coordinates for the object.
#         :type bbox: list
#         :param output_path_background_removed: Path to save the output image with background removed.
#         :type output_path_background_removed: str
#         :param smoothing_radius: Radius for the Gaussian blur used for edge smoothing.
#         :type smoothing_radius: int
#         :returns: None if successful, otherwise an error dictionary.
#         :rtype: None or dict
#         """
#         try:
#             image = cv2.cvtColor(cv2.imread(image_path), cv2.COLOR_BGR2RGB)
#             self.predictor.set_image(image)
#             input_box = np.array(bbox)
#             masks, _, _ = self.predictor.predict(box=input_box[None, :], multimask_output=False)
#             mask = masks[0]
#             # Convert mask to binary format
#             binary_mask = (mask > 0.5).astype(np.uint8)

#             # Create an edge mask using Canny edge detection
#             edges = cv2.Canny(binary_mask * 255, 100, 200)
            
#             # Dilate the edge mask to enhance edges
#             kernel = np.ones((dilation_kernel_size, dilation_kernel_size), np.uint8)
#             dilated_edges = cv2.dilate(edges, kernel, iterations=1)
            
#             # Create a smooth border by applying Gaussian blur to the dilated edges
#             blurred_edges = cv2.GaussianBlur(dilated_edges, (0, 0), edge_smooth_radius)
            
#             # Normalize blurred edges to range [0, 255]
#             normalized_edges = np.clip(blurred_edges, 0, 255).astype(np.uint8)
            
#             # Create an RGBA image (add alpha channel)
#             rgba_image = cv2.cvtColor(image, cv2.COLOR_RGB2RGBA)
#             rgba_image[:, :, 3] = binary_mask * 255
            
#             # Combine the smoothed edges with the alpha channel
#             rgba_image[:, :, 3] = np.maximum(rgba_image[:, :, 3], normalized_edges)

#             # Convert to PIL Image to save with transparency
#             pil_image = Image.fromarray(rgba_image)
#             pil_image.save(output_path_background_removed)
            
#             return None  # Return None if successful

#         except Exception as e:
#             return {"error_type": "Background Removal Error", "details": str(e)}


#     def generate_sticker(self, image_url):
#         """
#         Generate a sticker from the image at the given URL.

#         :param image_url: URL of the image to be processed.
#         :type image_url: str
#         :returns: Dictionary containing the sticker URL or an error dictionary.
#         :rtype: dict
#         """
#         try:
#             timestamp = StickerManager.get_timestamp()
#             image_path = os.path.join(self.img_folder, f"{timestamp}_image.jpg")
#             output_path_sticker = os.path.join(self.sticker_folder, f"{timestamp}_masked_area_sticker.png")

#             # Download the image
#             download_result = StickerManager.download_image(image_url, self.img_folder)
#             if isinstance(download_result, dict):
#                 return download_result

#             image_path = download_result

#             # Predict bounding box
#             bbox = self.predict(image_path)
#             if isinstance(bbox, dict):
#                 return bbox

#             # Process image for sticker
#             sticker_result = self.process_img(image_path, bbox, output_path_sticker)
#             if isinstance(sticker_result, dict):
#                 return sticker_result

#             # Upload sticker to S3
#             StickerManager.upload_to_s3(output_path_sticker, self.s3_bucket_name, f"sticker/{timestamp}_masked_area_sticker.png", content_type='image/png')

#             # Generate presigned URL for sticker
#             sticker_url = StickerManager.generate_presigned_url(self.s3_bucket_name, f"sticker/{timestamp}_masked_area_sticker.png")
#             if isinstance(sticker_url, dict):
#                 return sticker_url

#             # # Clean up local files
#             StickerManager.clean_local_files(image_path, output_path_sticker)

#             return {"sticker_url": sticker_url}

#         except Exception as e:
#             return {"error_type": "StickerGenerationError", "details": str(e)}

#     def remove_background(self, image_url):
#         """
#         Remove the background from the image at the given URL.

#         :param image_url: URL of the image to be processed.
#         :type image_url: str
#         :returns: Dictionary containing the URL of the background-removed image or an error dictionary.
#         :rtype: dict
#         """
#         try:
#             timestamp = StickerManager.get_timestamp()
#             image_path = os.path.join(self.img_folder, f"{timestamp}_image.jpg")
#             output_path_background_removed = os.path.join(self.bg_removed_folder, f"{timestamp}_background_removed.png")

#             # Download the image
#             download_result = StickerManager.download_image(image_url, self.img_folder)
#             if isinstance(download_result, dict):
#                 return download_result

#             image_path = download_result

#             # Predict bounding box
#             bbox = self.predict(image_path)
#             if isinstance(bbox, dict):
#                 return bbox

#             # Remove background
#             bg_remove_result = self.remove_background_and_save(image_path, bbox, output_path_background_removed)
#             if isinstance(bg_remove_result, dict):
#                 return bg_remove_result

#             # Upload background-removed image to S3
#             StickerManager.upload_to_s3(output_path_background_removed, self.s3_bucket_name, f"bg_removed/{timestamp}_background_removed.png", content_type='image/png')

#             # Generate presigned URL for background-removed image
#             bg_removed_url = StickerManager.generate_presigned_url(self.s3_bucket_name, f"bg_removed/{timestamp}_background_removed.png")
#             if isinstance(bg_removed_url, dict):
#                 return bg_removed_url

#             # # Clean up local files
#             StickerManager.clean_local_files(image_path, output_path_background_removed)

#             return {"bg_removed_url": bg_removed_url}

#         except Exception as e:
#             return {"error_type": "BackgroundRemovalError", "details": str(e)}





import os
import numpy as np
import cv2
from ultralytics import YOLO
from segment_anything import sam_model_registry, SamPredictor
from PIL import Image
from sticker_file_operation import StickerManager

class StickerProcessor:
    """
    A class to handle sticker processing including object detection, background removal,
    and sticker generation using YOLO and SAM models.

    :param yolo_model_path: Path to the YOLO model file.
    :type yolo_model_path: str
    :param sam_checkpoint_path: Path to the SAM model checkpoint file.
    :type sam_checkpoint_path: str
    :param sam_model_type: Type of the SAM model to use.
    :type sam_model_type: str
    :param s3_bucket_name: Name of the S3 bucket for storing and retrieving images.
    :type s3_bucket_name: str
    """
    
    def __init__(self, yolo_model_path, sam_checkpoint_path, sam_model_type, s3_bucket_name):
        """
        Initialize the StickerProcessor with the paths to the models and the S3 bucket name.

        :param yolo_model_path: Path to the YOLO model file.
        :type yolo_model_path: str
        :param sam_checkpoint_path: Path to the SAM model checkpoint file.
        :type sam_checkpoint_path: str
        :param sam_model_type: Type of the SAM model to use.
        :type sam_model_type: str
        :param s3_bucket_name: Name of the S3 bucket for storing and retrieving images.
        :type s3_bucket_name: str
        """
        print("Initializing StickerProcessor...")
        self.yolo_model_path = yolo_model_path
        self.sam_checkpoint_path = sam_checkpoint_path
        self.sam_model_type = sam_model_type
        self.s3_bucket_name = s3_bucket_name

        # Load YOLO model
        self.model = YOLO(yolo_model_path)

        # Load SAM model
        sam = sam_model_registry[sam_model_type](checkpoint=sam_checkpoint_path)
        self.predictor = SamPredictor(sam)

        # Define root directory for saving images and stickers
        self.root_dir = os.path.dirname(os.path.abspath(__file__))
        self.img_folder = os.path.join(self.root_dir, "img")
        self.sticker_folder = os.path.join(self.root_dir, "sticker")
        self.bg_removed_folder = os.path.join(self.root_dir, "bg_removed")


        try:
            print("inside try...")
            # Ensure base directories exist
            os.makedirs(self.img_folder, exist_ok=True)
            os.makedirs(self.sticker_folder, exist_ok=True)
            os.makedirs(self.bg_removed_folder, exist_ok=True)
        except Exception as e:
            return {"error_type": "file_making_error", "details": str(e)}

    def _ensure_directories(self, *dirs):
        """
        Ensure that specified directories exist.

        :param dirs: Directories to be checked and created if necessary.
        :type dirs: str
        """
        for dir_path in dirs:
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)

    def predict(self, image_path):
        """
        Predict the bounding box of objects in the given image using YOLO.

        :param image_path: Path to the image file.
        :type image_path: str
        :returns: List of bounding boxes for detected objects or an error dictionary.
        :rtype: list or dict
        """
        try:
            results = self.model.predict(image_path, save=False, verbose=False)
            if not results:
                raise Exception(f"No prediction result from the model for {image_path}")

            for result in results:
                boxes = result.boxes
            bbox = boxes.xyxy.tolist()[0]
            return bbox
        except Exception as e:
            return {"error_type": "error", "details": str(e)}

    def process_img(self, image_path, bbox, output_path_segmented, border_thickness=10):
        """
        Process the image to create a sticker by applying the mask to the image.

        :param image_path: Path to the input image file.
        :type image_path: str
        :param bbox: Bounding box coordinates for the object.
        :type bbox: list
        :param output_path_segmented: Path to save the output sticker image.
        :type output_path_segmented: str
        :param border_thickness: Thickness of the border around the object.
        :type border_thickness: int
        :returns: None if successful, otherwise an error dictionary.
        :rtype: None or dict
        """
        try:
            print("Bro, inside process image")
            self._ensure_directories(os.path.dirname(output_path_segmented))

            image = cv2.cvtColor(cv2.imread(image_path), cv2.COLOR_BGR2RGB)
            self.predictor.set_image(image)
            input_box = np.array(bbox)
            masks, _, _ = self.predictor.predict(box=input_box[None, :], multimask_output=False)
            mask = masks[0]
            # Convert mask to binary format
            binary_mask = (mask > 0.5).astype(np.uint8)
            rgba_image = cv2.cvtColor(image, cv2.COLOR_RGB2RGBA)
            rgba_image[:, :, 3] = (mask * 255).astype(np.uint8)

            # Dilate the mask to create a border around the object
            kernel = np.ones((border_thickness, border_thickness), np.uint8)
            dilated_mask = cv2.dilate(binary_mask, kernel, iterations=1)
            
            # Create the border by subtracting the original mask from the dilated mask
            border_mask = dilated_mask - binary_mask

            # Apply white border where the border_mask is set
            rgba_image[border_mask == 1] = [255, 255, 255, 255]  # White color with full opacity

            pil_image = Image.fromarray(rgba_image)
            pil_image.save(output_path_segmented)
            return None  # Return None if successful
        except Exception as e:
            return {"error_type": "Sticker Generation Error", "details": str(e)}

    def remove_background_and_save(self, image_path, bbox, output_path_background_removed, edge_smooth_radius=2, dilation_kernel_size=10):
        """
        Remove the background from the image, apply edge smoothing, and save the result.

        :param image_path: Path to the input image file.
        :type image_path: str
        :param bbox: Bounding box coordinates for the object.
        :type bbox: list
        :param output_path_background_removed: Path to save the output image with background removed.
        :type output_path_background_removed: str
        :param edge_smooth_radius: Radius for the Gaussian blur used for edge smoothing.
        :type edge_smooth_radius: int
        :param dilation_kernel_size: Size of the kernel used for dilation.
        :type dilation_kernel_size: int
        :returns: None if successful, otherwise an error dictionary.
        :rtype: None or dict
        """
        try:
            self._ensure_directories(os.path.dirname(output_path_background_removed))

            image = cv2.cvtColor(cv2.imread(image_path), cv2.COLOR_BGR2RGB)
            self.predictor.set_image(image)
            input_box = np.array(bbox)
            masks, _, _ = self.predictor.predict(box=input_box[None, :], multimask_output=False)
            mask = masks[0]
            # Convert mask to binary format
            binary_mask = (mask > 0.5).astype(np.uint8)

            # Create an edge mask using Canny edge detection
            edges = cv2.Canny(binary_mask * 255, 100, 200)
            
            # Dilate the edge mask to enhance edges
            kernel = np.ones((dilation_kernel_size, dilation_kernel_size), np.uint8)
            dilated_edges = cv2.dilate(edges, kernel, iterations=1)
            
            # Create a smooth border by applying Gaussian blur to the dilated edges
            blurred_edges = cv2.GaussianBlur(dilated_edges, (0, 0), edge_smooth_radius)
            
            # Normalize blurred edges to range [0, 255]
            normalized_edges = np.clip(blurred_edges, 0, 255).astype(np.uint8)
            
            # Create an RGBA image (add alpha channel)
            rgba_image = cv2.cvtColor(image, cv2.COLOR_RGB2RGBA)
            rgba_image[:, :, 3] = binary_mask * 255
            
            # Combine the smoothed edges with the alpha channel
            rgba_image[:, :, 3] = np.maximum(rgba_image[:, :, 3], normalized_edges)

            # Convert to PIL Image to save with transparency
            pil_image = Image.fromarray(rgba_image)
            pil_image.save(output_path_background_removed)
            
            return None  # Return None if successful

        except Exception as e:
            return {"error_type": "Background Removal Error", "details": str(e)}

    def generate_sticker(self, image_url):
        """
        Generate a sticker from the image at the given URL.

        :param image_url: URL of the image to be processed.
        :type image_url: str
        :returns: Dictionary containing the sticker URL or an error dictionary.
        :rtype: dict
        """
        try:

            print("inside gen sticker try block")
            timestamp = StickerManager.get_timestamp()
            image_path = os.path.join(self.img_folder, f"{timestamp}_image.jpg")
            output_path_sticker = os.path.join(self.sticker_folder, f"{timestamp}_masked_area_sticker.png")

            # Download the image
            download_result = StickerManager.download_image(image_url, self.img_folder)
            if isinstance(download_result, dict):
                return download_result

            image_path = download_result

            # Predict bounding box
            bbox = self.predict(image_path)
            if isinstance(bbox, dict):
                return bbox

            # Ensure sticker folder exists
            self._ensure_directories(self.sticker_folder)

            # Process image for sticker
            sticker_result = self.process_img(image_path, bbox, output_path_sticker)
            if isinstance(sticker_result, dict):
                return sticker_result

            # Upload sticker to S3
            StickerManager.upload_to_s3(output_path_sticker, self.s3_bucket_name, f"sticker/{timestamp}_masked_area_sticker.png", content_type='image/png')

            # Generate presigned URL for sticker
            sticker_url = StickerManager.generate_presigned_url(self.s3_bucket_name, f"sticker/{timestamp}_masked_area_sticker.png")
            if isinstance(sticker_url, dict):
                return sticker_url

            # Clean up local files
            try:
                StickerManager.clean_local_files(image_path, output_path_sticker)
            except Exception as e:
                print(f"Error cleaning local files: {str(e)}")

            return {"sticker_url": sticker_url}

        except Exception as e:
            return {"error_type": "StickerGenerationError", "details": str(e)}

    def remove_background(self, image_url):
        """
        Remove the background from the image at the given URL.

        :param image_url: URL of the image to be processed.
        :type image_url: str
        :returns: Dictionary containing the URL of the background-removed image or an error dictionary.
        :rtype: dict
        """
        try:
            timestamp = StickerManager.get_timestamp()
            image_path = os.path.join(self.img_folder, f"{timestamp}_image.jpg")
            output_path_background_removed = os.path.join(self.bg_removed_folder, f"{timestamp}_background_removed.png")

            # Download the image
            download_result = StickerManager.download_image(image_url, self.img_folder)
            if isinstance(download_result, dict):
                return download_result

            image_path = download_result

            # Predict bounding box
            bbox = self.predict(image_path)
            if isinstance(bbox, dict):
                return bbox

            # Ensure bg_removed folder exists
            self._ensure_directories(self.bg_removed_folder)

            # Remove background
            bg_remove_result = self.remove_background_and_save(image_path, bbox, output_path_background_removed)
            if isinstance(bg_remove_result, dict):
                return bg_remove_result

            # Upload background-removed image to S3
            StickerManager.upload_to_s3(output_path_background_removed, self.s3_bucket_name, f"bg_removed/{timestamp}_background_removed.png", content_type='image/png')

            # Generate presigned URL for background-removed image
            bg_removed_url = StickerManager.generate_presigned_url(self.s3_bucket_name, f"bg_removed/{timestamp}_background_removed.png")
            if isinstance(bg_removed_url, dict):
                return bg_removed_url

            # Clean up local files
            try:
                StickerManager.clean_local_files(image_path, output_path_background_removed)
            except Exception as e:
                print(f"Error cleaning local files: {str(e)}")

            return {"bg_removed_url": bg_removed_url}

        except Exception as e:
            return {"error_type": "BackgroundRemovalError", "details": str(e)}
