# Chinny_Virtual Fashion Assistant

> **An AI-powered virtual fashion assistant that provides personalized clothing recommendations using computer vision.**

## Overview

**Chinny_VFA** is an early prototype of a virtual fashion assistant developed to explore how computer vision and recommendation systems can be applied to personalized fashion discovery.

The prototype analyzes a user's uploaded full-body image, identifies a body-shape category, and provides clothing-style recommendations based on the selected fashion category.

The project was developed as an initial **proof of concept (PoC)** to test the viability of the idea and understand how users could interact with an AI-assisted fashion recommendation system.

> **Note:** This repository contains the early prototype used to validate the product concept. A more advanced version of Chinny_VFA is currently under development. Details of the current development version are intentionally not included in this repository.

---

# Problem

Choosing clothing styles can be challenging when users are unsure which silhouettes and styles may work well with their body proportions.

As a fashion entrepreneur, I explored how AI and computer vision could be used to make personalized fashion discovery more accessible.

The prototype was built to answer a simple question:

> **Can computer vision be used to analyze a user's body shape and generate relevant fashion recommendations?**

---

# How It Works

The prototype follows a simple workflow:

```text id="f8o9q4"
Upload Full-Body Photo
          ↓
   Image Processing
          ↓
   Body Shape Detection
          ↓
 Select Fashion Category
          ↓
 Style Recommendations
          ↓
 Fabric Information & Price
```

### Supported Categories

* **Casual**
* **Corporate / Office**
* **Traditional / Wedding**

Recommendations include relevant clothing styles as well as information about suggested fabrics and estimated fabric prices per yard.

---

# Computer Vision

The prototype uses image-processing and computer-vision techniques to analyze an uploaded image and determine a corresponding body-shape category.

The body-shape detection functionality is implemented in:

```text id="v0j5j3"
detect_shape.py
```

The recommendation component then uses the resulting body-shape classification.

---

# Recommendation System

The recommendation component maps the detected body-shape category and selected fashion category to relevant outfit recommendations.

The recommendation logic is implemented in:

```text id="w9w6l1"
recommend.py
```

The prototype demonstrates how structured recommendation logic can be combined with computer-vision output to create a personalized fashion experience.

---

# My Role

## Developer

I conceived and developed Chinny_VFA as a fashion-technology product, combining my experience in fashion with my work in AI and software development.

My work on this prototype included:

* Developing the body-shape detection functionality
* Building the recommendation logic
* Integrating image processing with the recommendation workflow
* Developing the Flask backend
* Connecting the application's components
* Building the user interaction flow
* Deploying the prototype for live testing
* Collecting feedback to inform subsequent product development

---

# 🛠️ Technology Stack

| Area            | Technology                      |
| --------------- | ------------------------------- |
| Programming     | Python                          |
| Backend         | Flask                           |
| Computer Vision | OpenCV / image-processing tools |
| Recommendation  | Python                          |
| Frontend        | HTML, CSS, JavaScript           |
| Deployment      | Render                          |
| Version Control | Git, GitHub                     |

---

# 📁 Project Structure

```text id="b0s5p2"
Chinny_Virtual_Fashion_Assistant/
│
├── Data/
├── Static/
├── templates/
│
├── app.py
├── detect_shape.py
├── recommend.py
├── feedback_store.py
├── reward_model.py
├── requirements.txt
├── Procfile
└── gunicorn.conf.py
```

### Key Components

**`app.py`**
Main Flask application.

**`detect_shape.py`**
Body-shape detection and image-processing functionality.

**`recommend.py`**
Fashion recommendation logic.

**`feedback_store.py`**
Handles feedback collected from the application.

**`reward_model.py`**
Contains the prototype's feedback/reward-model component.

**`templates/`**
HTML templates and user-interface pages.

**`Static/`**
CSS, JavaScript, images, and other frontend assets.

---

# 🚀 Current Status

### Early Prototype / Proof of Concept

The prototype is deployed and available for demonstration.

### Prototype capabilities

* ✅ Full-body image upload
* ✅ Body-shape detection
* ✅ Fashion category selection
* ✅ Style recommendations
* ✅ Casual recommendations
* ✅ Corporate / Office recommendations
* ✅ Traditional / Wedding recommendations
* ✅ Fabric information
* ✅ Fabric price information
* ✅ Feedback functionality

### Known Limitations

The prototype's body-shape detection can be affected by:

* Image quality
* Camera angle
* Body positioning
* Clothing
* Lighting
* Image-processing limitations

For best results, users should upload a clear, full-body image.

---

# 🔗 Project Link

**🌐 Live Prototype:**
https://chinny-virtual-fashion-assistant.onrender.com/

---

# 👩🏾‍💻 Developer

## Chinedu Eucharia Joseph

 **AI/ML Developer | Fashion Technology**

Chinny_VFA combines my background in **fashion entrepreneurship** with my interest in **Artificial Intelligence, computer vision, and product development**.

**Skills demonstrated:**
Computer Vision · AI/ML · Python · Flask · Recommendation Systems · Product Development · Web Development

---

## ⚠️ Prototype Disclaimer

This repository contains an early experimental prototype and is intended for demonstration and development purposes.

Body-shape detection and recommendations should not be interpreted as objective judgments about a person's body or appearance. Fashion recommendations are exploratory and intended to support, not dictate, individual style choices.
