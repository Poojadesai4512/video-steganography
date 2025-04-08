from flask import Flask, render_template, request, flash, redirect, url_for
import cv2
import numpy as np
from Crypto.Cipher import Blowfish
from Crypto.Util.Padding import pad, unpad
import os

# Initialize Flask application
app = Flask(__name__)
app.secret_key = "supersecretkey"

# Reference DNA numerically
reference_DNA = {'00': 'A', '01': 'T', '10': 'C', '11': 'G'}

def process_video(video_path, text_message):
    print("Received video path:", video_path)
    print("Received text message:", text_message)
    return video_path

# Function for Blowfish encryption
def blowfish_encrypt(text, key):
    cipher = Blowfish.new(key, Blowfish.MODE_ECB)
    padded_text = pad(text.encode(), Blowfish.block_size)
    encrypted_text = cipher.encrypt(padded_text)
    return encrypted_text

# Function for Blowfish decryption
def blowfish_decrypt(cipher_text, key):
    cipher = Blowfish.new(key, Blowfish.MODE_ECB)
    decrypted_padded_text = cipher.decrypt(cipher_text)
    decrypted_text = unpad(decrypted_padded_text, Blowfish.block_size)
    return decrypted_text.decode()

# Function to convert binary to fake DNA
def binary_to_fake_DNA(binary_string):
    fake_DNA = ''
    for i in range(0, len(binary_string), 2):
        pair = binary_string[i:i + 2]
        fake_DNA += reference_DNA[pair]
    return fake_DNA

# Function to apply DNA complementary rule to binary string
def apply_DNA_complementary_rule(binary_string):
    complement_pairs = {'0': '1', '1': '0'}
    complemented_binary_string = ''.join(complement_pairs[bit] for bit in binary_string)
    return complemented_binary_string

# Function to encrypt cipher text to fake DNA
def encrypt_to_fake_DNA(cipher_text):
    binary_text = ''.join(format(byte, '08b') for byte in cipher_text)
    complemented_binary_text = apply_DNA_complementary_rule(binary_text)
    fake_DNA_text = binary_to_fake_DNA(complemented_binary_text)
    return fake_DNA_text

# Convert DNA sequence to binary string
def dna_to_binary(dna_sequence):
    binary_string = ""
    for nucleotide in dna_sequence:
        if nucleotide == 'A':
            binary_string += '00'
        elif nucleotide == 'T':
            binary_string += '01'
        elif nucleotide == 'C':
            binary_string += '10'
        elif nucleotide == 'G':
            binary_string += '11'
    return binary_string

# Function to convert fake DNA to binary
def fake_DNA_to_binary(fake_DNA):
    binary_string = ''
    for char in fake_DNA:
        for key, value in reference_DNA.items():
            if value == char:
                binary_string += key
                break
    return binary_string

# Function to apply inverse DNA complementary rule to binary string
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

def frame_selection(video_path):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("Error: Unable to open video")
        return None

    complex_frame_indices = []
    ret, prev_frame = cap.read()
    if not ret:
        print("Error: Unable to read first frame")
        return None

    prev_frame_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
    frame_index = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        dct_prev = cv2.dct(np.float32(prev_frame_gray))
        dct_curr = cv2.dct(np.float32(frame_gray))

        mean_prev = np.mean(dct_prev)
        mean_curr = np.mean(dct_curr)

        if abs(mean_curr - mean_prev) > 0.001:
            complex_frame_indices.append(frame_index)

        prev_frame_gray = frame_gray.copy()
        frame_index += 1

    cap.release()
    return complex_frame_indices

def embed_data_in_frame(frame, data):
    flattened_frame = frame.flatten()
    data_index = 0

    for i in range(len(flattened_frame)):
        if data_index >= len(data):
            break

        lsb = flattened_frame[i] & 1
        new_lsb = int(data[data_index])
        flattened_frame[i] = (flattened_frame[i] & ~1) | new_lsb
        data_index += 1

    return flattened_frame.reshape(frame.shape)

def embed_length_in_frame(frame, length):
    # Convert length to binary
    length_binary = format(length, '032b')  # 32 bits for length
    return embed_data_in_frame(frame, length_binary)

def embedding(video_path, message, key):
    indices = frame_selection(video_path)
    input_video = cv2.VideoCapture(video_path)

    fps = input_video.get(cv2.CAP_PROP_FPS)
    frame_width = int(input_video.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(input_video.get(cv2.CAP_PROP_FRAME_HEIGHT))

    fourcc = cv2.VideoWriter_fourcc('F', 'F', 'V', '1')
    output_video = cv2.VideoWriter('output.avi', fourcc, fps, (frame_width, frame_height))

    encrypted_text = blowfish_encrypt(message, key.encode())
    DNA_sequence = encrypt_to_fake_DNA(encrypted_text)
    binary_sequence = dna_to_binary(DNA_sequence)
    data_length = len(binary_sequence)
    print('Data length:', data_length)

    frame_index = indices[0]
    while input_video.isOpened():
        ret, frame = input_video.read()
        if not ret:
            break

        if frame_index == indices[0]:
            # Embed the length first
            frame_with_length = embed_length_in_frame(frame.copy(), data_length)
            output_video.write(frame_with_length)

            # Embed the binary sequence
            frame_with_dna = embed_data_in_frame(frame.copy(), binary_sequence)
            output_video.write(frame_with_dna)
        else:
            output_video.write(frame)

        frame_index += 1

    input_video.release()
    output_video.release()
    cv2.destroyAllWindows()
    return encrypted_text

def extract_data_from_frame_ver(frame, data_length):
    ebin = ''
    flattened_frame = frame.flatten()

    for i in range(data_length):
        lsb = flattened_frame[i] & 1
        ebin += str(lsb)

    print("Extracted binary data:", ebin[:data_length])
    return ebin

def extract_length_from_frame(frame):
    length_binary = extract_data_from_frame_ver(frame, 32)  # Read 32 bits for length
    return int(length_binary, 2)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        video_file = request.files['video']
        message = request.form['message']
        key = request.form['key']

        if not video_file or not message or not key:
            flash('Please fill in all fields', 'error')
            return redirect(url_for('index'))

        video_path = os.path.join('static', video_file.filename)
        video_file.save(video_path)

        try:
            output_path = embedding(video_path, message, key)
            flash(f'Success! Encrypted video saved', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            flash(f'Encryption failed: {e}', 'error')
            return redirect(url_for('index'))

    return render_template('index_new.html')

# Run Flask app
if __name__ == '__main__':
    app.run(debug=False)
