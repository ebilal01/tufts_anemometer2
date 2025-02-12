from flask import Flask, render_template, jsonify
import json
import datetime

app = Flask(__name__)

message_history = []

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/live-data', methods=['GET'])
def live_data():
    message_data = {
        "latitude": 42.3601,
        "longitude": -71.0589,
        "temperature_cj_c": 22.5,
        "sent_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "altitude": 150
    }

    message_history.append(message_data)
    return jsonify(message_data)

@app.route('/history', methods=['GET'])
def history():
    return jsonify(message_history)

@app.route('/message-history', methods=['GET'])
def message_history_route():
    return jsonify(message_history)

@app.route('/download-history', methods=['GET'])
def download_history():
    filename = "message_history.csv"
    with open(filename, "w") as f:
        f.write("Received Time,Latitude,Longitude,Temperature (°C),Altitude\n")
        for msg in message_history:
            f.write(f"{msg['sent_time']},{msg['latitude']},{msg['longitude']},{msg['temperature_cj_c']},{msg['altitude']}\n")
    return jsonify({"message": f"History downloaded as {filename}"})


if __name__ == '__main__':
    app.run(debug=True)

 







