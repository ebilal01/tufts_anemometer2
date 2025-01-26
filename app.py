from flask import Flask, render_template, jsonify, request, Response
import random
import time
import json
import os
from flask_socketio import SocketIO
import eventlet
import csv

app = Flask(__name__, static_folder="static", template_folder="templates")

flight_history = []

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
        message_parts = dict(part.split(":") for part in decoded_message.split(","))
        latitude = float(message_parts.get("lat", 0))
        longitude = float(message_parts.get("lon", 0))
        altitude = float(message_parts.get("alt", 0))
        timestamp = time.time()

        flight_history.append({
            "timestamp": timestamp,
            "latitude": latitude,
            "longitude": longitude,
            "altitude": altitude
        })
    except Exception as e:
        return "FAILED,15,Error parsing message data", 400

    return "OK,0"

@app.route('/live-data', methods=['GET'])
def live_data():
    if flight_history:
        return jsonify(flight_history[-1])
    return jsonify({})

@app.route('/animation-data', methods=['GET'])
def animation_data():
    return jsonify({
        "rotation": random.uniform(0, 360),
        "position": {"x": random.uniform(-10, 10), "y": random.uniform(-10, 10), "z": random.uniform(-10, 10)},
        "force": {"x": random.uniform(0, 1), "y": random.uniform(0, 1), "z": random.uniform(0, 1)}
    })

@app.route('/download-history', methods=['GET'])
def download_history():
    csv_file = "flight_history.csv"
    keys = ["timestamp", "latitude", "longitude", "altitude"]
    with open(csv_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(flight_history)
    return Response(
        open(csv_file, "r"),
        mimetype="text/csv",
        headers={"Content-disposition": f"attachment; filename={csv_file}"}
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

