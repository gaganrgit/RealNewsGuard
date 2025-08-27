RealNewsGuard/
├── .gitignore
├── README.md
├── test_api.py
│
├── backend/
│   ├── .env
│   ├── .env.example
│   ├── main.py
│   ├── requirements.txt
│   ├── test_prediction.py
│   ├── api/
│   ├── models/
│   ├── static/
│   └── utils/
│
└── frontend/
├── public/
└── src/


---

## ⚙️ Setup and Run Instructions (For VSCode)

Follow these steps precisely to get the application running.

### Step 1: Backend Setup

1.  **Open the `RealNewsGuard` folder in VSCode.**
2.  **Open a new terminal** in VSCode (`Terminal` > `New Terminal`).
3.  **Navigate to the backend directory:**
    ```bash
    cd backend
    ```
4.  **Create and activate a Python virtual environment.**
    ```bash
    # Create the environment
    python -m venv venv
    # Activate it (on Windows)
    .\venv\Scripts\activate
    # Activate it (on macOS/Linux)
    source venv/bin/activate
    ```
5.  **Install the required dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
6.  **Set up your NewsAPI Key:**
    * In the `backend` folder, rename `.env.example` to `.env`.
    * Open the `.env` file and paste in your unique API key: `NEWS_API_KEY="your_key_here"`

7.  **Download NLTK data** for text processing. Run this command once:
    ```bash
    python -c "import nltk; nltk.download('punkt', quiet=True); nltk.download('stopwords', quiet=True); nltk.download('averaged_perceptron_tagger', quiet=True)"
    ```

8.  **Run the backend server:**
    ```bash
    uvicorn main:app --reload
    ```
    Your backend API is now live at `http://127.0.0.1:8000`.

### Step 2: Frontend Setup

1.  **Open a *new* VSCode terminal.**
2.  **Navigate to the frontend directory:**
    ```bash
    cd frontend
    ```
3.  **Start a simple web server.**
    ```bash
    python -m http.server 8080
    ```
4.  **Access the application:** Open your web browser and go to: `http://localhost:8080/public/`
