from flask import Flask, render_template, jsonify, request
import time
import random

app = Flask(__name__, static_folder="static", template_folder="templates")

# In-memory store for demonstration purposes
flight_history = []

# Simulated force vector data
def generate_simulated_vectors():
    return {
        "force": {
            "x": random.uniform(-1, 1),
            "y": random.uniform(-1, 1),
            "z": random.uniform(-1, 1)
        },
        "rotation": random.uniform(0, 360),
        "position": {
            "x": random.uniform(-10, 10),
            "y": random.uniform(-10, 10),
            "z": random.uniform(-10, 10)
        }
    }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/rockblock', methods=['POST'])
def handle_rockblock():
    imei = request.args.get('imei')
    username = request.args.get('username')
    password = request.args.get('password')

    if imei != "300434065264590" or username != "myUser" or password != "myPass":
        return "FAILED,10,Invalid login credentials", 400

    data = request.args.get('data')
    if not data:
        return "FAILED,16,No data provided", 400

    try:
        decoded_message = bytes.fromhex(data).decode('utf-8')
    except ValueError:
        return "FAILED,14,Could not decode hex data", 400

    try:
        message_parts = dict(part.split(":") for part in decoded_message.split(","))
        latitude = float(message_parts.get("lat", 0))
        longitude = float(message_parts.get("lon", 0))
        altitude = float(message_parts.get("alt", 0))
        timestamp = time.time()  # Add timestamp

        flight_history.append({
            "timestamp": timestamp,
            "latitude": latitude,
            "longitude": longitude,
            "altitude": altitude
        })

    except Exception as e:
        print("Error parsing message:", e)
        return "FAILED,15,Error parsing message data", 400

    return "OK,0"

@app.route('/live-data', methods=['GET'])
def live_data():
    # Generate simulated arrow vector data
    telemetry_data = generate_simulated_vectors()

    # Add latest flight data if available
    if flight_history:
        latest = flight_history[-1]
        telemetry_data.update({
            "latitude": latest["latitude"],
            "longitude": latest["longitude"],
            "altitude": latest["altitude"],
            "timestamp": latest["timestamp"]
        })

    return jsonify(telemetry_data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

