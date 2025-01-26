from flask import Flask, render_template, jsonify, request, Response
import random
import time
import json
import os
from flask_socketio import SocketIO
import eventlet
import csv

app = Flask(__name__)

# In-memory store for demonstration purposes
flight_history = []

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

    print(f"IMEI: {imei}, Decoded Message: {decoded_message}")

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

        print(f"Latitude: {latitude}, Longitude: {longitude}, Altitude: {altitude}")
    except Exception as e:
        print("Error parsing message:", e)
        return "FAILED,15,Error parsing message data", 400

    return "OK,0"

@app.route('/live-data', methods=['GET'])
def live_data():
    if flight_history:
        return jsonify(flight_history[-1])  # Latest data
    return jsonify({})

@app.route('/history', methods=['GET'])
def load_flight_history():
    return jsonify(flight_history)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)


