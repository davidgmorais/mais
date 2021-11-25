import math
import cv2
import dlib
from imutils import face_utils

LEFT_IDX = face_utils.FACIAL_LANDMARKS_IDXS['left_eye']
RIGHT_IDX = face_utils.FACIAL_LANDMARKS_IDXS['right_eye']


def eye_aspect_ratio(eye):
    """
    Calculates the Eye Aspect Ratio of an eye

    Auxiliary function used to calculate the EAR (eye aspect ratio) of an eye using its landmarks by calculating the
    euclidean distance between the two sets of vertical landmarks divided by the double of the euclidean distance
    between the horizontal set of landmarks

    :param eye: landmarks of the eye whose EAR we want to calculate
    :return: the EAR of the eye
    """

    A = math.sqrt(math.pow((eye[1][0] - eye[5][0]), 2) + math.pow((eye[1][1] - eye[5][1]), 2))
    B = math.sqrt(math.pow((eye[2][0] - eye[4][0]), 2) + math.pow((eye[2][1] - eye[4][1]), 2))

    return (A + B) / (2 * math.sqrt(math.pow((eye[0][0] - eye[3][0]), 2) + math.pow((eye[0][1] - eye[3][1]), 2)))


class FaceDetector:
    """ Class representing the face detector """

    def __init__(self, ar_threshold, blinks=1):
        """
        Initializes a FaceDetector instance

        :param ar_threshold: threshold under which the detector consider that the eye is closed using its EAR
        :param blinks: number of blinks that are necessary to confirm liveliness
        """

        self.face_detector = cv2.CascadeClassifier('./configs/haarcascade_frontalface_default.xml')
        self.landmark_predictor = dlib.shape_predictor('./configs/shape_predictor_68_face_landmarks.dat')
        self.ar_threshold = ar_threshold
        self.blinks_needed = blinks
        self.counter = 0    # consecutive nr of frames on which the eyes are closed
        self.total = 0      # number of blinks
        self.faces_on_frame = 0

    def detect(self, img):
        """
        Detects faces of an image

        This method is used to detect the faces on a given image by first detecting all the faces in the frame and for
        each checks its liveliness (by the blinking of the eyes) to ensure that there is no photo being placed in front
        of the camera. This is done using the landmark predictor to predict the position of the eyes and calculating
        their ear, whose variation allows us to infer that they are blinking. Every time the number of the faces on the
        frame changes, this verification is done again.

        :param img: frame on which to detect the faces
        :return: image with a square delimiting the found faces, list of matrices with the region of interest in
        grayscale and list of matrices with region of interest in color.
        """

        img = cv2.flip(img, 1)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = self.face_detector.detectMultiScale(
            gray,
            scaleFactor=1.2,
            minNeighbors=5,
            minSize=(20, 20)
        )

        # check variation of number of faces in the frame
        if self.faces_on_frame != len(faces):
            self.faces_on_frame = len(faces)
            print(f"Faces on the frame: {self.faces_on_frame}")
            self.total = 0

        roi_gray = []
        roi_color = []

        for (x, y, w, h) in faces:
            # verify liveliness
            shape = self.landmark_predictor(gray, dlib.rectangle(x, y, x + w, y + h))
            shape = face_utils.shape_to_np(shape)

            left_eye = shape[LEFT_IDX[0]: LEFT_IDX[1]]
            left_eye_ear = eye_aspect_ratio(left_eye)
            right_eye = shape[RIGHT_IDX[0]: RIGHT_IDX[1]]
            right_eye_ear = eye_aspect_ratio(right_eye)

            ear = (right_eye_ear + left_eye_ear) / 2

            if ear < self.ar_threshold:
                self.counter += 1
            else:
                # if 3 consecutive frames with eyes closed, then consider it a blink
                if self.counter >= 3:
                    self.total += 1
                self.counter = 0

            if self.total >= self.blinks_needed:
                # draw square on the frame
                cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)

                roi_gray.append(gray[y:y + h, x:x + w])
                roi_color.append(img[y:y + h, x:x + w])

        return img, roi_gray, roi_color
