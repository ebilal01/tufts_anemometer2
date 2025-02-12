from flask import Flask, render_template, jsonify, request, Response
import random
import time
import json
import os
from flask_socketio import SocketIO
import eventlet
import csv
import struct
import datetime
from flask_cors import CORS

app = Flask(__name__, static_folder="static", template_folder="templates")
CORS(app)  # Enable CORS for all routes
socketio = SocketIO(app, cors_allowed_origins="*")

# In-memory store for demonstration purposes
message_history = []

# Path to store flight data history
FLIGHT_HISTORY_FILE = 'flight_data.json'

# Ensure flight data is saved to a file
def save_flight_data(flight_data):
    if not os.path.exists(FLIGHT_HISTORY_FILE):
        with open(FLIGHT_HISTORY_FILE, 'w') as f:
            json.dump([], f)  # Initialize the file with an empty list

    with open(FLIGHT_HISTORY_FILE, 'r') as f:
        flight_history = json.load(f)

    # Append the new flight data
    flight_history.append(flight_data)

    # Save the updated flight history
    with open(FLIGHT_HISTORY_FILE, 'w') as f:
        json.dump(flight_history, f)

# Load the flight history from the file
def load_flight_history():
    if not os.path.exists(FLIGHT_HISTORY_FILE):
        return []  # No history available
    with open(FLIGHT_HISTORY_FILE, 'r') as f:
        return json.load(f)

@app.route('/')
def index():
    return render_template('index.html')  # Ensure this matches the frontend file

@app.route('/rockblock', methods=['POST'])
def handle_rockblock():
    imei = request.args.get('imei')
    data = request.args.get('data')

    print(f"Received POST /rockblock - IMEI: {imei}, Data: {data}")

    if imei != "300434065264590":
        print("Invalid credentials")
        return "FAILED,10,Invalid login credentials", 400

    if not data:
        print("No data provided")
        return "FAILED,16,No data provided", 400

    try:
        byte_data = bytearray.fromhex(data)

        # Ensure it's exactly 50 bytes (sensor data size)
        if len(byte_data) != 50:
            print(f"Message size is incorrect: {len(byte_data)} bytes")
            return "FAILED,17,Invalid message length", 400

        # Unpack the 50 bytes as per the specified structure
        sensor_data = struct.unpack('IhfH16h', byte_data)  # Correct format for 50 bytes
        sensor_data = list(sensor_data)

        # Scale values where necessary (based on your sensor data format)
        # Example: Scale the sensor data (lat/lon/alt, etc.) if needed
        sensor_data[2] /= 1000000  # Latitude scale
        sensor_data[3] /= 1000000  # Longitude scale
        sensor_data[4] /= 10  # Altitude scale, if needed
        # Sensor data from 16th byte to 50th byte
        for i in range(5, 21):
            sensor_data[i] /= 10  # Adjust scaling if necessary

        # Sent time (Unix timestamp converted to UTC)
        sent_time_utc = datetime.datetime.fromtimestamp(sensor_data[0], datetime.UTC).strftime('%Y-%m-%dT%H:%M:%SZ')

        # Extract extra message text if there are any
        extra_message = ""
        if len(byte_data) > 50:
            extra_bytes = byte_data[50:]  
            extra_message = extra_bytes.decode('utf-8', errors='ignore').strip()  # Convert extra bytes to text

        # Store data for live retrieval
        message_data = {
            "received_time": datetime.datetime.utcnow().isoformat() + "Z",
            "sent_time": sent_time_utc,
            "unix_epoch": sensor_data[0],
            "siv": sensor_data[1],
            "latitude": sensor_data[2],
            "longitude": sensor_data[3],
            "altitude": sensor_data[4],
            "sensor_data": sensor_data[5:],  # Store sensor data from byte 16 onwards
            "message": extra_message if extra_message else "No extra message"
        }

        # Append to history
        message_history.append(message_data)

        print(f"Processed and stored message: {message_data}")

        return "OK,0"

    except Exception as e:
        print("Error processing data:", e)
        return "FAILED,15,Error processing message data", 400




@app.route('/live-data', methods=['GET'])
def get_live_data():
    return jsonify(message_history[-1] if message_history else {"message": "No data received yet"})

@app.route('/flight-data', methods=['GET'])
def live_data():
    # Ensure message_data exists or is simulated correctly
    data = {
        "latitude": message_history[-1]["latitude"] if message_history else "No data",
        "longitude": message_history[-1]["longitude"] if message_history else "No data",
        "timestamps": message_history[-1]["sent_time"] if message_history else "No data",
        "altitudes": message_history[-1]["altitude"] if message_history else "No data"
    }
    return jsonify(data)

@app.route('/history', methods=['GET'])
def load_flight_history():
    return jsonify(message_history)

@app.route('/download-history', methods=['GET'])
def download_history():
    if not message_history:
        return "No data available", 404

    def generate_csv():
        fieldnames = message_history[0].keys()
        yield ','.join(fieldnames) + '\n'  # Header row
        for row in message_history:
            yield ','.join(str(row[field]) for field in fieldnames) + '\n'  # Data rows

    return Response(generate_csv(), mimetype='text/csv',
                    headers={"Content-Disposition": "attachment; filename=flight_history.csv"})

@app.route('/message-history', methods=['GET'])
def message_history_endpoint():
    return jsonify(message_history) if message_history else jsonify([])

@app.route("/animation-data", methods=['GET'])
def animation_data():
    # Example live telemetry data
    telemetry_data = {
        "rotation": random.uniform(0, 360),  # Rotation in degrees
        "position": {
            "x": random.uniform(-5, 5),
            "y": random.uniform(-5, 5),
            "z": random.uniform(-5, 5)
        },
        "force": {
            "x": random.uniform(0, 10),
            "y": random.uniform(0, 10),
            "z": random.uniform(0, 10)
        }
    }
    return jsonify(telemetry_data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

 







