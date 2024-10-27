from flask import Flask, render_template, request, jsonify
import cv2
import face_recognition
import datetime
import threading

app = Flask(__name__)

# قائمة الأطفال المسجلين
known_face_encodings = []  # هنا تضع بيانات الوجوه المشفرة
known_face_names = []  # أسماء الأطفال

def start_camera(camera_ip):
    video_capture = cv2.VideoCapture(f"rtsp://{camera_ip}")

    while True:
        ret, frame = video_capture.read()
        if not ret:
            print("تعذر الاتصال بالكاميرا.")
            break

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        for face_encoding in face_encodings:
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
            name = "Unknown"

            if True in matches:
                index = matches.index(True)
                name = known_face_names[index]
                print(f"{name} دخل في: {datetime.datetime.now()}")

@app.route('/')
def home():
    return '''
        <h1>مرحبًا في نظام إدارة صالة الألعاب</h1>
        <input type="text" id="cameraIp" placeholder="أدخل IP الكاميرا">
        <button onclick="startMonitoring()">بدء المراقبة</button>
        <h2 id="status">الحالة: غير متصل</h2>

        <script>
            function startMonitoring() {
                const ip = document.getElementById('cameraIp').value;
                fetch('/start', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ camera_ip: ip })
                })
                .then(response => response.json())
                .then(data => {
                    document.getElementById('status').innerText = 'الحالة: متصل';
                    console.log(data);
                });
            }
        </script>
    '''

@app.route('/start', methods=['POST'])
def start_monitoring():
    camera_ip = request.json['camera_ip']
    threading.Thread(target=start_camera, args=(camera_ip,)).start()
    return jsonify({"status": "Monitoring started!"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
