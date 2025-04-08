# Video Steganography with Fake DNA and Complex Frame
A secure and intelligent steganography system that hides secret messages in video files using Blowfish encryption, fake DNA encoding, and complex frame selection using DCT. Built with Python and Flask, this project provides a web interface for easy encryption and decryption.

## Features
- Hide text inside videos using encryption and fake DNA encoding
- Uses Blowfish encryption for high security
- Converts cipher text into fake DNA using binary rules
- Embeds data in complex frames selected using DCT analysis
- Extracts and decrypts data from stego videos
- Easy-to-use web interface built with Flask

## Technologies used
- Python
- OpenCV
- NumPy
- Flask
- HTML

## Installation
Follow these steps to run the project locally:
1. **Clone the repository:**
   '''bash
   git clone
   https://github.com/poojadesai4512/video-steganography.git
   cd Video-Steganography

1. Create a virtual environment
   python -m venv venv source venv/bin/activate  #on windows: venv\scripts\activate
   
1. Install dependencies:
   pip install -r requirements.txt

How to Run
-Start Encryption app:
  python app.py
  visit: http://localhost:50000
  
-Start Decryption app:
  python decrypt_app.py
  visit: http://localhost:50000

## Usage
Embedding (Encryption):
1. Open the encryption app.
2. Upload a video file.
3. Enter the Secret message and encryption key.
4. Download the stego video.

Extraction (Decryption):
1. Open the decryption app.
2. Upload the stego video.
3. Enter the same encryption key.
4. View the extracted hidden message.

## Floder Structure
video-steganography
--app.py         # Main Flask app (Encryption)
--decrypt_app.py  # Flask app for decryption
--templates/
   -index_new.html  # Upload & embed UI
   -index_decryption_new.html   # Upload & decrypt UI
   -result_new.html    # decrypted message result page
--Static/  # Uploaded and processed videos
--Uploads  # Temporary uploads
--requirements.txt  # dependencies
--README.md  # project documentation   
