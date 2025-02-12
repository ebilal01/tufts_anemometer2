from flask import Flask, jsonify, request
import datetime

app = Flask(__name__)

# In-memory storage for messages
message_history = []

@app.route('/live-data', methods=['GET'])
def get_live_data():
    return jsonify(message_history[-1] if message_history else {"message": "No data received yet"})

@app.route('/history', methods=['GET'])
def get_message_history():
    return jsonify(message_history)

@app.route('/send-message', methods=['POST'])
def send_message():
    global message_history

    data = request.json
    if 'sent_time' not in data:
        return jsonify({"error": "Missing sent_time"}), 400

    sent_time_utc = datetime.datetime.strptime(data['sent_time'], "%Y-%m-%dT%H:%M:%S.%fZ")
    received_time = datetime.datetime.utcnow().isoformat() + "Z"

    message_data = {
        "received_time": received_time,
        "sent_time": sent_time_utc,
        "latitude": data.get('latitude', 0),
        "longitude": data.get('longitude', 0),
        "altitude": data.get('altitude', 0),
        "temperature_cj_c": data.get('temperature_cj_c', 0),
        # Add more fields as required
    }

    message_history.append(message_data)
    return jsonify({"status": "Message received"}), 200

@app.route('/download-history', methods=['GET'])
def download_history():
    import csv
    import io
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=message_history[0].keys())
    writer.writeheader()
    writer.writerows(message_history)
    output.seek(0)
    return output.getvalue(), 200, {'Content-Type': 'text/csv'}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
 







