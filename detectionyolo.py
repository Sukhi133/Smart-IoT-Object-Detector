import cv2
from ultralytics import YOLO
import os

# Load YOLOv8 model
yolo = YOLO('yolov8s.pt')

# Function to generate distinct colors for classes
def getColours(cls_num):
    base_colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]
    color_index = cls_num % len(base_colors)
    increments = [(1, -2, 1), (-2, 1, -1), (1, -1, 2)]
    color = [
        (base_colors[color_index][i] + increments[color_index][i] * (cls_num // len(base_colors))) % 256
        for i in range(3)
    ]
    return tuple(color)

# Ask user to choose input mode
mode = input("Choose input mode: (c)amera, (f)ile, or (i)p camera? ").strip().lower()

if mode == 'c':
    cap = cv2.VideoCapture(0)

elif mode == 'i':
    ip_url = input("Enter ESP32-CAM stream URL (e.g., http://192.168.x.x:81/stream): ").strip()
    cap = cv2.VideoCapture(ip_url)

elif mode == 'f':
    file_path = input("Enter image or video file path: ").strip()
    if not os.path.isfile(file_path):
        print("Error: File not found.")
        exit()

    # If image
    if file_path.lower().endswith(('.png', '.jpg', '.jpeg')):
        frame = cv2.imread(file_path)
        results = yolo.track(frame, stream=True)

        for result in results:
            classes_names = result.names
            for box in result.boxes:
                if box.conf[0] > 0.4:
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    cls = int(box.cls[0])
                    color = getColours(cls)
                    label = f'{classes_names[cls]} {box.conf[0]:.2f}'
                    cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                    cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)

        cv2.imshow('YOLO Image Detection', frame)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        exit()

    # If video
    elif file_path.lower().endswith(('.mp4', '.avi', '.mov', '.mkv')):
        cap = cv2.VideoCapture(file_path)

    else:
        print("Unsupported file format.")
        exit()
else:
    print("Invalid input. Choose 'c', 'f', or 'i'.")
    exit()

# Check if capture is open
if not cap.isOpened():
    print("Error: Could not open video source.")
    exit()

# Run detection loop
while True:
    ret, frame = cap.read()
    if not ret:
        break

    results = yolo.track(frame, stream=True)

    for result in results:
        classes_names = result.names
        for box in result.boxes:
            if box.conf[0] > 0.4:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                cls = int(box.cls[0])
                color = getColours(cls)
                label = f'{classes_names[cls]} {box.conf[0]:.2f}'
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)

    cv2.imshow('YOLO Detection', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
