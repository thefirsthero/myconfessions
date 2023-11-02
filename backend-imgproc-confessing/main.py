import datetime
import shutil
import time
import uuid
from connection import db
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import FileResponse
import requests
import uvicorn
import os
import json
from typing import List
import imghdr 
from image_processing import extract_and_reformat_text
from text_processing import filter_text, clean_and_format_text, extract_series_and_part, split_and_clean_text
from ocr_functions import extract_text_with_tesseract
from fastapi.middleware.cors import CORSMiddleware
from models import Confession
from os import environ as env
from os import remove
from firebase_admin import storage, firestore
import tempfile

# Create an instance of FastAPI to handle routes
app = FastAPI()

'''The below section allows specific ip addresses to make requests'''
# Get allowed servers from env file
react_app_origin_1 = env['MY_VARIABLE_1']
react_app_origin_2 = env['MY_VARIABLE_2']

# Configure CORS to allow requests from your React app's origin
origins = [
    react_app_origin_1,
    react_app_origin_2
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins, # Add your React app's origin(s) here
    allow_methods=["*"],  # Allow all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

# We access the 'users' collection in the database (Firestore instance)
confessions = db.collection(u'confessions')

# Define the behavior for the http://127.0.0.1:8000/ route with the GET method
@app.get("/")
async def root():
    # Using confessions.get(), which belongs to Firebase, we retrieve all users from the list
    confessionsRef = confessions.get()
    # Create a dictionary to return in JSON format
    confessionsJson = {}
    # Iterate through the list of confessions
    for confession in confessionsRef:
        # Add each retrieved confession to the dictionary
        confessionsJson[confession.id] = confession.to_dict()
    # Return the dictionary
    return confessionsJson

# Define the behavior for the http://127.0.0.1:8000/addConfession route with the POST method
@app.post("/addConfession")
async def addConfession(confession_obj: Confession): 
    try:
        # Get the count of existing documents in the 'confessions' collection
        confessions_count = len(list(confessions.stream()))
        
        # Set the 'id' field of the new document to the count + 1
        confession_obj.id = str(confessions_count + 1)
        
        # Create a new Confession document in Firestore
        new_confession = confessions.add(confession_obj.dict())
        return {'status': 200, 'message': 'Confession added successfully'}
    except Exception as e:
        return {'status': 500, 'error': str(e)}

# Import the necessary modules
from collections import defaultdict

# Create a dictionary to store filenames and their counts
uploaded_filenames = defaultdict(int)

# API endpoint to upload images
@app.post("/upload-images/")
async def upload_images(images: List[UploadFile]):
    try:
        # Initialize an empty list to store image URLs
        image_urls = []

        # Iterate through the uploaded image files
        for image in images:
            # Check if the file is a valid image type
            if imghdr.what(image.file) is not None:
                # Extract the original filename from the uploaded file
                original_filename = image.filename

                # Check if the original filename has been uploaded before
                if uploaded_filenames[original_filename] >= 1:
                    raise Exception(f"Image '{original_filename}' has already been uploaded.")

                # Increment the count for the original filename
                uploaded_filenames[original_filename] += 1

                # Upload the image to Firebase Storage with its original filename
                bucket = storage.bucket()
                blob = bucket.blob(original_filename)
                blob.upload_from_file(image.file, content_type=image.content_type)

                # Get the download URL for the uploaded image
                image_url = blob.generate_signed_url(
                    expiration=datetime.timedelta(days=1),
                    method="GET"
                )

                # Save the image URL to Firestore
                image_doc = {
                    'url': image_url,
                    'filename': original_filename
                }

                # Add the image document to the 'images' collection in Firestore
                db.collection('images').add(image_doc)

                # Append the image URL to the list
                image_urls.append(image_url)
            else:
                # Raise an exception if the file is not an image
                raise Exception(f"{image.filename} is not an image file")

        return {'status': 200, 'message': 'Images uploaded successfully', 'image_urls': image_urls}
    except Exception as e:
        return {'status': 500, 'error': str(e)}


# API endpoint to return the OCR text of the images uploaded
@app.get("/process-images/")
async def process_images():
    try:
        # Initialize video data as an empty list
        video_data = []

        # Get a reference to the Firestore collection
        db = firestore.client()
        images_ref = db.collection('images')

        # Retrieve all image documents from Firestore
        images = images_ref.stream()

        # Create a temporary directory for downloading images
        temp_dir = tempfile.mkdtemp(prefix='image_download_')

        # Process each image in Firestore
        for image in images:
            image_data = image.to_dict()
            if image_data:
                image_url = image_data.get('url')

                # Generate a unique, short filename
                image_filename = f"image_{str(uuid.uuid4())}"

                image_local_path = os.path.join(temp_dir, image_filename)

                # Download the image from its original URL
                original_image_response = requests.get(image_url)
                if original_image_response.status_code == 200:
                    with open(image_local_path, "wb") as local_image_file:
                        local_image_file.write(original_image_response.content)

                # Call the function with the chosen OCR library
                extracted_text = extract_and_reformat_text(image_local_path, extract_text_with_tesseract)

                # Text processing
                series, part = extract_series_and_part(extracted_text)
                cleaned_text = filter_text(extracted_text)
                cleaned_text = clean_and_format_text(cleaned_text)
                cleaned_text = split_and_clean_text(cleaned_text)

                # Update the video data and append it
                video_data.append({
                    "series": series,
                    "part": part,
                    "outro": "Visit www.myconfessions.co.za to anonymously confess",
                    "text": cleaned_text
                })

                # Delete the temporary image
                os.remove(image_local_path)

        # Sort video_data by the 'part' field in ascending order
        video_data = sorted(video_data, key=lambda x: int(x["part"]))

        # Write video_data to a JSON file
        video_json_path = os.path.join(temp_dir, 'video.json')
        with open(video_json_path, 'w', encoding='utf-8') as video_json_file:
            json.dump(video_data, video_json_file, ensure_ascii=False, indent=4)

        return FileResponse(video_json_path, headers={"Content-Disposition": "attachment; filename=video.json"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Endpoint to get a JSON list of filenames from the Firestore images collection
@app.get("/list-images/")
async def list_images():
    try:
        # Get a reference to the Firestore collection
        db = firestore.client()
        images_ref = db.collection('images')

        # Retrieve all image documents from Firestore
        images = images_ref.stream()

        # Extract filenames from Firestore documents
        filenames = [image.to_dict().get('filename') for image in images]

        return {"files": filenames}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# API endpoint to delete a specific image from Firestore and Storage
@app.delete("/delete-image/{filename}")
async def delete_image(filename: str):
    try:
        # Get a reference to the Firestore collection
        db = firestore.client()
        images_ref = db.collection('images')

        # Query Firestore to find the image with the specified filename
        query = images_ref.where('filename', '==', filename)
        results = query.stream()

        # Check if the image with the specified filename exists
        found = False
        for image in results:
            found = True
            image_data = image.to_dict()

            # Decrement the count for the deleted image's filename
            original_filename = image_data.get('filename')
            if original_filename in uploaded_filenames:
                uploaded_filenames[original_filename] -= 1

            # Delete the document in Firestore
            image.reference.delete()

            # Delete the corresponding image in the Firebase Storage bucket
            bucket = storage.bucket()
            blob = bucket.blob(filename)
            blob.delete()

        if found:
            return {"message": f"Image '{filename}' deleted successfully from Firestore and Storage"}
        else:
            return {"message": f"Image '{filename}' not found in the database"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# API endpoint to delete all images stored on the server and clear the uploaded_filenames map
@app.delete("/delete-images/")
async def delete_images():
    try:
        # Clear the entire uploaded_filenames map
        uploaded_filenames.clear()

        # Get a reference to the Firestore collection
        db = firestore.client()
        images_ref = db.collection('images')

        # Retrieve all image documents from Firestore
        images = images_ref.stream()

        # Check if the 'images' collection is not empty
        images_exist = False

        for image in images:
            images_exist = True
            image_data = image.to_dict()
            if image_data:
                filename = image_data.get('filename')

                # Delete the document in Firestore
                image.reference.delete()

                # Delete the corresponding object from the Firebase Storage bucket
                bucket = storage.bucket()
                blob = bucket.blob(filename)
                blob.delete()

        if images_exist:
            return {"message": "All images deleted successfully, and the uploaded_filenames map is cleared"}
        else:
            return {"message": "No images found to delete, and the uploaded_filenames map is cleared"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Healthcheck Endpoint
@app.get("/healthcheck")
async def healthcheck():
    return {"status": "ok"}
