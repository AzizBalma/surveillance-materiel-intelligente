import cv2
import numpy as np
import os
import logging
from datetime import datetime
import time

from config.paths import *


class Camera:
    def __init__(self, alert_system, model_path=str(VISION_MODEL), conf_threshold=0.5):
        self.alert_system = alert_system
        self.model_path = model_path
        self.conf_threshold = conf_threshold
        self.names = ["Person"]

        # Charger le modèle ONNX
        try:
            self.net = cv2.dnn.readNetFromONNX(self.model_path)
            self.net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
            self.net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)
            logging.info("✅ Modèle ONNX chargé avec succès.")
        except Exception as e:
            logging.error(f"❌ Erreur de chargement du modèle ONNX : {e}")
            self.net = None

        os.makedirs("visualizations", exist_ok=True)
        self.capture = cv2.VideoCapture(0)
        self.last_detection_time = 0
        self.cooldown = 10  # secondes entre 2 alertes
        self.frame = None

    def yolo_postprocess(self, pred, img_shape, conf_thres=0.25, iou_thres=0.45):
        pred = pred.transpose(1, 0)
        boxes, scores = [], []
        img_h, img_w = img_shape[:2]

        for det in pred:
            x, y, w, h, conf = det
            if conf < conf_thres:
                continue
            x1 = int((x - w/2) * img_w / 640)
            y1 = int((y - h/2) * img_h / 640)
            x2 = int((x + w/2) * img_w / 640)
            y2 = int((y + h/2) * img_h / 640)
            boxes.append([x1, y1, x2 - x1, y2 - y1])
            scores.append(float(conf))

        idxs = cv2.dnn.NMSBoxes(boxes, scores, conf_thres, iou_thres)
        results = []
        if len(idxs) > 0:
            for i in idxs.flatten():
                results.append((boxes[i], scores[i]))
        return results

    def run_loop(self):
        if not self.net or not self.capture.isOpened():
            logging.error("❌ Impossible de démarrer la caméra ou le modèle.")
            return

        logging.info("🎥 Caméra active — détection en cours...")

        while True:
            ret, frame = self.capture.read()
            if not ret:
                continue

            blob = cv2.dnn.blobFromImage(frame, 1/255.0, (640, 640), swapRB=True, crop=False)
            self.net.setInput(blob)
            out = self.net.forward()[0]
            detections = self.yolo_postprocess(out, frame.shape, 0.35, 0.5)

            detected_person = False
            for (x, y, w, h), score in detections:
                if score >= self.conf_threshold:
                    detected_person = True
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    cv2.putText(frame, f"Person {score:.2f}", (x, y - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

            if detected_person:
                now = time.time()
                if now - self.last_detection_time > self.cooldown:
                    self.last_detection_time = now
                    img_path = os.path.join("visualizations", f"detection_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg")
                    cv2.imwrite(img_path, frame)

                    # 🔧 Adapter à ton système
                    self.alert_system.add_alert(
                        "camera_intrusion",
                        "Personne détectée (confiance > 50%)",
                        {"image_path": img_path}
                    )

                    logging.warning(f"🚨 Personne détectée — Image sauvegardée : {img_path}")

            self.frame = frame
            time.sleep(0.1)

    def generator_mjpeg(self):
        while True:
            if self.frame is not None:
                ret, buffer = cv2.imencode('.jpg', self.frame)
                frame = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            time.sleep(0.05)

