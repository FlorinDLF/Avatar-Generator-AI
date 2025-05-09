# AI Avatar Generator

A web application that allows users to create personalized AI avatars from a photo or live camera input. The app offers four distinct styles: **cartoon**, **anime**, **Pixar**, and **3D**. Powered by **OpenAI GPT-4o**, **DALL·E 3**, and **DeepFace**, the application analyzes facial features and automatically generates detailed prompts for avatar creation.

## Features

- Upload a photo or capture one using your webcam
- Automatically detect age, gender, emotion, ethnicity using DeepFace
- Generate avatars in one of four unique styles:
  - Cartoon
  - Anime
  - Pixar-like
  - 3D realistic
- Live image preview and animated loading state
- Download generated avatar in high resolution

## 🛠Technologies Used

- **Frontend:** React, HTML5, CSS3
- **Backend:** Python (Flask), OpenAI API, DeepFace, requests
- **AI Services:**
  - OpenAI GPT-4o (vision + text analysis)
  - DALL·E 3 (image generation)
  - DeepFace (facial attribute extraction)
- **Multimedia Processing:** base64, webcam capture, FormData uploads

## Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-username/avatar-generator.git

2. **Backend Setup (Python):**
  Install required packages:
    ```bash
    pip install flask flask-cors openai deepface python-dotenv requests
  Create a .env file with your OpenAI key:
    OPENAI_API_KEY=your_openai_api_key_here
  Run the server:
    python app.py

4. **Frontend Setup (React):**
  Navigate to the frontend folder and install dependencies:
    ```bash
    npm install
  Run the development server:
    
    npm start

