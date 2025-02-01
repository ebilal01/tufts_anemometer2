from flask import Flask, render_template, jsonify, request, Response
import struct
import datetime
import csv

app = Flask(__name__, static_folder="static", template_folder="templates")

message_history = []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/rockblock', methods=['POST'])
def handle_rockblock():
    imei = request.args.get('imei')
    data = request.args.get('data')

    if imei != "300434065264590" or not data:
        return "FAILED", 400

    try:
        byte_data = bytearray.fromhex(data)
        sensor_data = struct.unpack('IhffHhhhhhhhhhhhhhhhh', byte_data[:50])
        sensor_data = list(sensor_data)

        for x in range(5, 12):
            sensor_data[x] /= 10  
        for x in range(12, 15):
            sensor_data[x] /= 1000  
        for x in range(15, 21):
            sensor_data[x] /= 100  

        message_data = {
            "received_time": datetime.datetime.utcnow().isoformat() + "Z",
            "latitude": sensor_data[2],
            "longitude": sensor_data[3],
            "altitude": sensor_data[4]
        }

        message_history.append(message_data)
        return "OK"

    except Exception:
        return "FAILED", 400

@app.route('/live-data')
def get_live_data():
    return jsonify(message_history[-1] if message_history else {"message": "No data yet"})

@app.route('/download-history')
def download_history():
    if not message_history:
        return "No data available", 404

    def generate_csv():
        fieldnames = message_history[0].keys()
        yield ','.join(fieldnames) + '\n'
        for row in message_history:
            yield ','.join(str(row[field]) for field in fieldnames) + '\n'

    return Response(generate_csv(), mimetype='text/csv')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)



