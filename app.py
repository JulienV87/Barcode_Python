import cv2
import numpy as np
from flask import Flask, render_template, Response, request, jsonify
from flask_socketio import SocketIO, emit
from pyzbar.pyzbar import decode

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

def gen_frames():
    cap = cv2.VideoCapture(0)
    while True:
        success, frame = cap.read()
        if not success:
            break
        else:
            # Decode barcodes in the frame
            barcodes = decode(frame)
            for barcode in barcodes:
                barcode_data = barcode.data.decode('utf-8')
                barcode_type = barcode.type
                # Emit barcode data to the client
                socketio.emit('barcode', {'data': barcode_data, 'type': barcode_type})
                # Draw rectangle around the barcode
                pts = np.array([barcode.polygon], np.int32)
                pts = pts.reshape((-1, 1, 2))
                cv2.polylines(frame, [pts], True, (0, 255, 0), 2)
                # Put barcode data and type on the frame
                pts2 = barcode.rect
                cv2.putText(frame, f'{barcode_data} ({barcode_type})', (pts2[0], pts2[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/scan', methods=['POST'])
def scan():
    if 'image' not in request.files:
        return jsonify([])
    file = request.files['image']
    img = cv2.imdecode(np.frombuffer(file.read(), np.uint8), cv2.IMREAD_COLOR)
    barcodes = decode(img)
    barcode_info = [barcode.data.decode('utf-8') for barcode in barcodes]
    return jsonify(barcode_info)

if __name__ == "__main__":
    socketio.run(app, debug=True)