import uvicorn
import os
import uuid
import shutil
import logging
from typing import Optional

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import aiofiles

# Import local modules
from models.prediction import predict_fake_news
from api.news_api import get_related_news
from api.news_verification import verify_news

# --- Basic Logging Configuration ---
# This sets up a logger to print informational messages and errors to the console.
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- FastAPI App Initialization ---
app = FastAPI(
    title="RealNewsGuard API",
    description="An API for detecting fake news by analyzing text and images.",
    version="1.1.0"
)

# --- CORS Middleware ---
# Allows the frontend (running on a different port) to communicate with this backend.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins for development purposes.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Directory Setup ---
# Ensures that the necessary directories for file uploads and static files exist.
os.makedirs("uploads", exist_ok=True)
os.makedirs("static/processed_images", exist_ok=True)

# --- Static File Mounting ---
# Makes the 'static' directory publicly accessible via the /static URL path.
app.mount("/static", StaticFiles(directory="static"), name="static")


# --- API Endpoints ---

@app.get("/", tags=["General"])
async def root():
    """
    Root endpoint that provides a welcome message and a link to the API documentation.
    """
    return {
        "message": "Welcome to the RealNewsGuard API",
        "documentation": "/docs"
    }

@app.post("/analyze", tags=["Analysis"])
async def analyze_news(
    headline: str = Form(...),
    content: str = Form(...),
    image: Optional[UploadFile] = File(None),
):
    """
    The main endpoint that analyzes a news article for authenticity.
    """
    image_path = None
    public_image_url = None

    try:
        # Step 1: Handle the image upload if one is provided.
        if image:
            # Basic validation to ensure the uploaded file is an image.
            if not image.content_type or not image.content_type.startswith("image/"):
                raise HTTPException(status_code=400, detail="Uploaded file is not a valid image.")

            # Create a unique filename to prevent conflicts.
            file_extension = os.path.splitext(image.filename)[1] if image.filename else '.jpg'
            image_name = f"{uuid.uuid4()}{file_extension}"
            image_path = os.path.join("uploads", image_name)
            
            # Asynchronously save the uploaded file to the 'uploads' directory.
            async with aiofiles.open(image_path, "wb") as out_file:
                file_content = await image.read()
                await out_file.write(file_content)
            
            # Copy the image to the 'static' directory to make it publicly accessible.
            processed_image_path = os.path.join("static", "processed_images", image_name)
            shutil.copy(image_path, processed_image_path)
            public_image_url = f"/static/processed_images/{image_name}"
            logging.info(f"Image saved and accessible at {public_image_url}")

        # Step 2: Call the core prediction logic.
        logging.info("Starting fake news prediction...")
        prediction_result = predict_fake_news(headline, content, image_path)
        
        # Step 3: Fetch related news from external sources.
        logging.info("Fetching related news articles...")
        related_news = get_related_news(headline)
        
        # Step 4: Scrape fact-checking websites.
        logging.info("Verifying against fact-checking sites...")
        verification_results = verify_news(headline)
        
        # Step 5: Assemble the final JSON response.
        result = {
            "prediction": prediction_result["prediction"],
            "confidence": prediction_result["confidence"],
            "explanation": prediction_result["explanation"],
            "related_news": related_news,
            "fact_checks": verification_results,
            "image_url": public_image_url,
            "detailed_features": prediction_result["features"] # For debugging and advanced frontend use.
        }
        
        return result
    
    except HTTPException as http_exc:
        # Re-raise FastAPI's own exceptions to ensure correct HTTP responses.
        raise http_exc
    except Exception as e:
        # Catch any other unexpected errors and return a generic 500 server error.
        logging.error(f"An error occurred in /analyze endpoint: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"An internal server error occurred: {str(e)}")
    finally:
        # Clean up the temporary uploaded file after processing to save disk space.
        if image_path and os.path.exists(image_path):
            os.remove(image_path)


# This block allows running the server directly from the command line with `python main.py`
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)