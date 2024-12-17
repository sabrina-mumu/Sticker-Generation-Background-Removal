# From Image to BG_Remove & Sticker_Generation
## Overview:
- This project develops the process of removing the background of an image using SAM and YOLOv8
- The YOLOv8 detects the object and SAM masks it and removes other things
- Then, edge sharpening is applied
- A white border is added for the sticker

## About:
- This project contains the api BG_Remove & Sticker_Generation

## Steps:
### Install necessary plugins
- Install virtual environment in the command prompt  `pip install virtualenv`
- Make a virtual environment in the directory  `python -m venv .venv`      (Here the environment name is .venv)
- Activate the environment  
	- For Windows `.venv\Scripts\activate`
	- For Unix `source .venv/bin/activate`
 - Download and install the necessary files  `pip install -r requirements.txt`

 - Download Files
 -  1. [yolov8n.pt](https://drive.google.com/file/d/1AK5o-PW-RDwN8wrxHVphsHM0mabLTRzf/view?usp=sharing)(Obj_Detection),
 -  2. [sam_vit_h_4b8939.pth](https://drive.google.com/file/d/1D4xlCWtZkoWKxWVcQf9qj9Kx4-If0NE-/view?usp=sharing)(For_Masking)


 ### Run the server
 <!-- - Run cmmand `uvicorn sticker_api:app --reload --host 192.168.68.104` -->
 - Run cmmand `uvicorn sticker_api:app --reload`
 - Go to this link `localhost:8000/upload` [post method]
 - UI can be load from here: `localhost:8000/docs`
 

