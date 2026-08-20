# Chinny_VFA — Virtual Fashion Assistant

Chinny_VFA is an AI-powered fashion assistant that helps users discover clothing styles based on their body shape.

> **Note:** This repository contains an early proof-of-concept version. A newer version is currently under development.

## Features

- Body-shape prediction from uploaded photos
- Style recommendations based on predicted body shape
- Casual, Corporate/Office, and Traditional/Wedding categories
- Fabric information and estimated price per yard
- User feedback

## How It Works

1. Upload a clear full-body photo.
2. The application predicts a body-shape category.
3. Select a fashion category.
4. Receive style recommendations.

## Technology

- Python
- Flask
- OpenCV
- HTML/CSS/JavaScript

## Project Structure

    Chinny_Virtual_Fashion_Assistant/
    │
    ├── Data/
    ├── Static/
    ├── templates/
    ├── app.py
    ├── detect_shape.py
    ├── recommend.py
    ├── feedback_store.py
    ├── reward_model.py
    ├── requirements.txt
    ├── Procfile
    └── gunicorn.conf.py

## Current Status

**Early Prototype / Proof of Concept**

The prototype is live and was developed to test the concept of AI-assisted fashion recommendations.

A newer version is currently under development.

## Known Limitation

The body-shape prediction model does not yet produce sufficiently reliable results across different images and conditions. Improving prediction accuracy is a key focus of the next version.

## Project

**Live Prototype:**  
https://chinny-virtual-fashion-assistant.onrender.com/

**Repository:**  
https://github.com/Ukayria/Chinny_Virtual_Fashion_Assistant

## Key Components

- **`app.py`** — Main Flask application
- **`detect_shape.py`** — Body-shape prediction functionality
- **`recommend.py`** — Style recommendation logic
- **`feedback_store.py`** — Feedback handling
- **`reward_model.py`** — Feedback/reward model component
- **`templates/`** — Application interface
- **`Static/`** — CSS, JavaScript, and visual assets
