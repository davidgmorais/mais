import sys
import getpass
import cv2

from face_detection import FaceDetector
from face_recognition import FaceRecognition

MAX_TRIES = 10


def detect_from_image(filename):
    """
    Detect faces from an image using the FaceDetector class and displays it using opencv (used to test the liveliness
    on photos)

    :param filename: image to detect faces from
    """

    img = cv2.imread(filename)
    face_detector = FaceDetector(0.3, 2)
    img = face_detector.detect(img)

    cv2.imshow('image', img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def detect_from_cam():
    """
    Detect faces from the camera video stream (used to test the face detection module)

    Similarly to detect_from_images, this function detects faces but instead of using a file, it loops through the
    frames from the webcam video stream, releasing it in the end. It also displays the found faces in the live video
    stream using opencv (which can be closed using 'q').
    """

    cap = cv2.VideoCapture(0)
    face_detector = FaceDetector(0.3, 2)

    while True:
        ret, img = cap.read()
        if img is None:
            print('No captured frame!')
            break

        img, _, _ = face_detector.detect(img)
        cv2.imshow('live feed', img)

        if cv2.waitKey(10) == 27:
            break

    cap.release()
    cv2.destroyAllWindows()


def register():
    """
    Function used to manually test the registration of a user

    Register a user by asking for input of an email and password. After making sure that a user with the same email
    does not exist, opens the camera and, using the FaceDetection modules, collects the sample size required from the
    FaceRecognition module consisting on greyscale images in regard to the region of interest od the user's face,
    converting them to a byte string and appending them to the 'collected' array If the number of faces in a frame
    varies, then the collection will start over. Once sampling is completed, the video capture is released and the
    method register of FaceRegister is called to register the user.
    """

    face_recognition = FaceRecognition()

    print("** User Registration **")
    email = input("E-mail: ")
    password = getpass.getpass("Password: ")

    if face_recognition.user_exists(email):
        print("This email is already in use")
        return

    cap = cv2.VideoCapture(0)
    face_detector = FaceDetector(0.3, 2)

    collected = []
    while True:
        ret, img = cap.read()
        if img is None:
            print('No captured frame!')
            break

        img, roi_gray, _ = face_detector.detect(img)
        cv2.imshow('live feed', img)

        if cv2.waitKey(10) == 27:
            break

        if len(roi_gray) != 1:
            if len(collected) > 0:
                print("Starting over, make sure you are the only person one in frame")
                collected = []
            continue

        elif len(roi_gray) > 0:
            roi_bytes = cv2.imencode('.jpg', roi_gray[0])[1].tobytes()  # Numpy one-dim array representative of the img
            collected.append(roi_bytes)

            if len(collected) == face_recognition.sample_size:
                print("Collection completing.")
                break

    cap.release()
    cv2.destroyAllWindows()

    if face_recognition.register(email, password, collected):
        print("User registered with success")


def auth():
    """
    Function used to manually test the authentication of a user

    Authenticates a user by first creating a FaceRecognition object and asking the user for its email. After that it
    start the video capture from the laptop camera. For every frame detects the face on screen using the  detect method
    from the FaceDetection module, extracts the greyscale region of interest (if there is one) and uses it to
    authenticate the user, using the authenticate method of the FaceRecognition. Closes the video capture from the
    live camera and the connection to the FaceRecognition.
    """

    face_recognition = FaceRecognition(confidence=65.0)

    email = input("E-mail: ")
    tries = 0

    cap = cv2.VideoCapture(0)
    face_detector = FaceDetector(0.3, 2)
    is_authenticated = False

    while not is_authenticated:
        ret, img = cap.read()
        if img is None:
            print('No captured frame!')
            break

        img, roi_gray, _ = face_detector.detect(img)
        cv2.imshow('live feed', img)

        if cv2.waitKey(10) == 27:
            break

        if len(roi_gray) == 0:
            continue

        for roi in roi_gray:
            if face_recognition.authenticate(email, roi):
                print("User authenticated, welcome!")
                is_authenticated = True
                break

        tries += 1
        if tries >= MAX_TRIES:
            print("\nFace authentication failed.")
            break

    cap.release()
    cv2.destroyAllWindows()
    face_recognition.close()


def main(_type):
    """
    Function used to test the functionalities while developing

    :param _type: action to be executed, can either be 'register' or 'auth'
    :return:
    """

    if _type == 'register':
        register()
    elif _type == 'auth':
        auth()
    else:
        print("[ERROR] Unknown action.")


if __name__ == "__main__":
    main(sys.argv[1])
