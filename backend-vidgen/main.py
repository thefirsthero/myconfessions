from fastapi import FastAPI
import subprocess
import os
import firebase_admin
from firebase_admin import credentials, firestore
from fastapi.responses import JSONResponse
from connection import db

app = FastAPI()

def run_populate_video_json():
    try:
        subprocess.run(["python", "populate_video_json.py"], check=True)
    except subprocess.CalledProcessError as e:
        return JSONResponse(content={"error": "Failed to run populate_video_json.py"}, status_code=500)

    return True

def is_video_json_empty():
    # Check if video.json exists and is not empty
    if os.path.exists("video.json") and os.path.getsize("video.json") > 0:
        return False
    return True

def generate_videos():
    # Check if video.json is empty
    if is_video_json_empty():
        return JSONResponse(content={"error": "video.json is empty or does not exist"}, status_code=500)

    try:
        subprocess.run(["python", "vidgen.py", "--model", "medium", "--tts", "en-US-ChristopherNeural"], check=True)
    except subprocess.CalledProcessError as e:
        return JSONResponse(content={"error": "Failed to generate videos"}, status_code=500)

    return True

def store_videos_in_firebase():
    # Get a list of video files in the 'output' directory
    video_files = [f for f in os.listdir("output") if f.endswith(".mp4")]

    for video_file in video_files:
        # Get the video name (removing the file extension)
        video_name = os.path.splitext(video_file)[0]

        try:
            # Read the video file as bytes
            with open(os.path.join("output", video_file), "rb") as video_content:
                # Upload the video to Firebase using the video name as the document ID
                db.collection("videos").document(video_name).set({"url": video_name, "content": video_content.read()})

        except Exception as e:
            return JSONResponse(content={"error": f"Failed to store video '{video_name}' in Firebase"}, status_code=500)

    return True

@app.get("/generate-videos/")
async def generate_and_store_videos():
    if run_populate_video_json() and generate_videos() and store_videos_in_firebase():
        return JSONResponse(content={"message": "Videos generated and stored in Firebase"}, status_code=200)
    else:
        return JSONResponse(content={"error": "Failed to run populate_video_json.py, generate videos, or store videos"}, status_code=500)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
