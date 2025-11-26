# Chinny: The Virtual Fashion Assistant

Chinny is a web app that helps people discover fashion styles that suit their body shapes. It makes choosing outfits faster and easier for both clients and tailors.

**Features**

* Detects body shape from a photo

- Recommends styles in three categories: Casual, Corporate/Office, Traditional/Wedding

- Shows fabrics used for each outfit, with price per yard

- Simplifies decisions for clients

- Streamlines communication between clients and tailors

**How it Works**

- Upload a clear full-body photo
- Select a style category
- Chinny detects your body shape and shows recommended styles, fabrics, and prices
- The recommendations appear as elegant cards with images and details for easy comparison.

**Future Plans**
- Designers and tailors can post their designs with price estimates
- Link to major style platforms like Pinterest for more inspiration
- Add a digital marketplace feature so clients can contact designers directly

**Installation**
- Clone the repository:
git clone https://github.com/Ukayria/Chinny_Virtual_Fashion_Assistant.git
- Navigate to the project folder:
cd Chinny_Virtual_Fashion_Assistant
- Create a virtual environment and activate it:
python -m venv venv
# Windows
venv\Scripts\activate
# Mac/Linux
source venv/bin/activate
- Install dependencies:
pip install -r requirements.txt
- Run the app:
python app.py
- Open your browser at http://127.0.0.1:5000/

**Folder Structure**
- app.py – Main Flask application
- detect_shape.py – Body shape detection logic
- recommend.py – Style recommendation logic
- static/ – CSS, JS, images
- templates/ – HTML files

# Note

❗ Upload clear full-body images for the best detection results

❗ Body shape detection may need improvements for more accurate edge detection
