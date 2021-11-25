#!/usr/bin/python3
import cv2


class ObjectDetection:
    # init the Object Detection instance with the configurations
    def __init__(self):
        self.class_names = []
        self.class_file = 'configs/coco.names'
        self.config_path = 'configs/ssd_mobilenet_v3_large_coco_2020_01_14.pbtxt'
        self.weight_path = 'configs/frozen_inference_graph.pb'

        with open(self.class_file, 'rt') as file:
            self.class_names = file.read().rstrip('\n').split('\n')
            file.close()

        self.net = cv2.dnn_DetectionModel(self.weight_path, self.config_path)
        self.net.setInputSize((320, 320))
        self.net.setInputScale(1.0 / 127.5)
        self.net.setInputMean((127.5, 127.5, 127.5))
        self.net.setInputSwapRB(True)

    # detect objects on an image, give the filename returns an image with a the name and a
    # rectangle surrounding the objects detected drawn on it
    def detect(self, file_name):
        img = cv2.imread(file_name)
        class_ids, confs, bbox = self.net.detect(img, confThreshold=0.5)

        print(class_ids, bbox)
        if len(class_ids) != 0:  #
            for class_id, confidence, box in zip(class_ids.flatten(), confs.flatten(), bbox):
                cv2.rectangle(img, box, color=(0, 255, 0), thickness=2)
                cv2.putText(img, self.class_names[class_id - 1].upper(), (box[0] + 10, box[1] + 30),
                            cv2.FONT_HERSHEY_COMPLEX, 1,
                            (0, 255, 0), 2)

        return img
