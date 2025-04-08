import cv2
import numpy as np
from flask import Flask, request, render_template, redirect, url_for
from werkzeug.utils import secure_filename
from Crypto.Cipher import Blowfish
from Crypto.Util.Padding import pad, unpad
import os

# Reference DNA numerically
reference_DNA = {'00': 'A', '01': 'T', '10': 'C', '11': 'G'}
UPLOAD_FOLDER = 'uploads'

# Initialize Flask app
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Blowfish decryption function
def blowfish_decrypt(cipher_text, key):
    cipher = Blowfish.new(key, Blowfish.MODE_ECB)
    decrypted_padded_text = cipher.decrypt(cipher_text)
    decrypted_text = unpad(decrypted_padded_text, Blowfish.block_size)
    return decrypted_text.decode()

# Function to extract data from video frames
def extract_data_from_frame_ver(frame, data_length):
    ebin = ''
    flattened_frame = frame.flatten()

    for i in range(data_length):
        lsb = flattened_frame[i] & 1
        ebin += str(lsb)

    return ebin

# Function to convert fake DNA to binary
def fake_DNA_to_binary(fake_DNA):
    binary_string = ''
    for char in fake_DNA:
        for key, value in reference_DNA.items():
            if value == char:
                binary_string += key
                break
    return binary_string

def extract_length_from_frame(frame):
    length_binary = extract_data_from_frame_ver(frame, 32)  # Read 32 bits for length
    return int(length_binary, 2)

# Function to convert binary to fake DNA
def binary_to_fake_DNA(binary_string):
    fake_DNA = ''
    for i in range(0, len(binary_string), 2):
        pair = binary_string[i:i + 2]
        fake_DNA += reference_DNA[pair]
    return fake_DNA

# Function to apply inverse DNA complementary rule
def apply_inverse_DNA_complementary_rule(binary_string):
    complemented_pairs = {'0': '1', '1': '0'}
    complemented_binary_string = ''.join(complemented_pairs[bit] for bit in binary_string)
    return complemented_binary_string

# Function to decrypt fake DNA to cipher text
def decrypt_fake_DNA(encrypted_fake_DNA):
    binary_text = fake_DNA_to_binary(encrypted_fake_DNA)
    complemented_binary_text = apply_inverse_DNA_complementary_rule(binary_text)
    decrypted_bytes = []
    for i in range(0, len(complemented_binary_text), 8):
        byte = complemented_binary_text[i:i + 8]
        decrypted_bytes.append(int(byte, 2))
    return bytes(decrypted_bytes)

# Function to extract hidden data from video file
def extraction(video_path):
    cap = cv2.VideoCapture(video_path)
    data_binary = ''
    data_length = None

    # Read the first frame to get length
    ret, first_frame = cap.read()
    if ret:
        data_length = extract_length_from_frame(first_frame)

    # Read remaining frames to extract data
    while cap.isOpened() and len(data_binary) < data_length:
        ret, frame = cap.read()
        if not ret:
            break
        data_binary += extract_data_from_frame_ver(frame, data_length - len(data_binary))

    cap.release()

    fake_DNA_sequence = binary_to_fake_DNA(data_binary[:data_length])
    decrypted_bytes = decrypt_fake_DNA(fake_DNA_sequence)
    return decrypted_bytes

@app.route('/')
def index():
    return render_template('index_decryption_new.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'video' not in request.files:
        return redirect(request.url)
    file = request.files['video']
    key = request.form.get('key')
    key_as_string = str(key)
    if file.filename == '':
        return redirect(request.url)
    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # Extract and decrypt message
        # key = "test1"
        extracted_message = extraction(filepath)
        decrypted_message = blowfish_decrypt(extracted_message, key_as_string.encode())

        # Render result page
        return render_template('result_new.html', decrypted_message=decrypted_message)

if __name__ == "__main__":
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(debug=True)
