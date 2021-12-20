import os
import uuid

import cryptography.exceptions
import mysql.connector
import cv2
import numpy as np
import hashlib
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding, hmac, hashes
from cryptography.hazmat.backends import default_backend


SAMPLE_SIZE = 30
config = {
    'host': 'localhost',
    'port': 3306,
    'user': 'admin',
    'password': 'pass',
    'database': 'mais'
}
# docker run --name=mais-db -p 3306:3306 -e MYSQL_ROOT_PASSWORD=_secret -e MYSQL_USER=admin -e MYSQL_PASSWORD=pass
# -e MYSQL_DATABASE=mais -d mysql/mysql-server:latest


def bytes_to_opencv(im_bytes):
    """
    Auxiliary function to convert a byte string into a grayscale opencv image

    :param im_bytes: byte representation of an image
    :return: numpy array representative of the image
    """

    im_arr = np.frombuffer(im_bytes, dtype=np.uint8)
    return cv2.imdecode(im_arr, flags=cv2.IMREAD_GRAYSCALE)


class FaceRecognition:
    """ Class representing the face recognition module """

    def __init__(self, confidence=0.0):
        """
        Initializes a FaceRecognition instance

        Contains an instance of the opencv LBPHFaceRecognition (which uses the Local Binary Patterns Histograms
        algorithm) and a connection to a database. If, upon instantiating an object, there is already data relative to
        users in said database, then it queries it and trains the recognizer with them, if not the recognizer is left
        untrained.

        :param confidence: threshold for the confidence that the authentication must have to succeed
        """

        self.__recognizer = cv2.face.LBPHFaceRecognizer_create()
        self.__conn = None
        self.sample_size = SAMPLE_SIZE
        self.confidence = confidence             # authentication confidence (false match rate / false non match rate)
        self.__connect()

        # directory to save encrypted data
        self.__data_dir = "data/"
        if not os.path.exists(self.__data_dir):
            os.mkdir(self.__data_dir)

        # keys for encryption and decryption
        self.__key = b'\xc4\x01!\xbc\xb7\x9e\xc6\xb8\xc4\x8f\xc9\xfb\xec\x84\xdf\xfd'
        self.__iv = b'\x91\xa2\x1f\xc1\x15\x89{\xe7\x87\xd9\xcdh\xef\xe1\xa9\xa7'
        self.__hash_key = b'\x11\x97\xe2\x9a\xd2n\xf7\xa2\xee\x0e\xbc\x89\xb6\x9d\x99\x89'

        # initialize AES cipher in CBC mode and PKCS7 padder
        self.__cipher = Cipher(algorithms.AES(self.__key), modes.CBC(self.__iv), default_backend())
        self.__padder = padding.PKCS7(algorithms.AES.block_size)  # block_size in bits

        if not self.__conn:
            return

        faces, ids = self.__get_faces_and_labels()
        if len(faces) == 0 or len(ids) == 0:
            return
        self.__recognizer.train(faces, np.asarray(ids))

    def __connect(self):
        """
        Private function to connect to the database
        """

        try:
            self.__conn = mysql.connector.connect(**config)
            print("Connection established")
        except mysql.connector.Error as err:
            print(err)

    def __get_faces_and_labels(self):
        """
        Private function to retrieve the stored images and labels from the database

        Retrieves all users from the database and stores them in the 'users' list. Then for every user retrieves all
        the images that belong to him stored in the filesystem (decrypting them and verifying their integrity),
        appending them to the list 'faces' and the user id (which will be used as label) to the list 'ids'.
        The computed list (faces and ids) are of equal size so that the id in ids[i] belong to the face in faces[i].

        :return: a list of images corresponding to faces, and a list of user ids to whom the faces belong to. If a
        connection to the database is not established, two empty lists wll be returned.
        """

        faces, ids = [], []
        if self.__conn:
            cursor = self.__conn.cursor()

            query = "SELECT id FROM USER;"
            cursor.execute(query)
            users = [user[0] for user in cursor.fetchall()]
            cursor.reset()

            query = "SELECT image, mac FROM IMAGE WHERE user_id = %s;"
            for user in users:
                cursor.execute(query, [user])
                for image in cursor.fetchall():

                    face = self.__decrypt_and_verify(image[0], image[1], user)
                    if face is None:
                        continue

                    faces.append(face)
                    ids.append(user)

                cursor.reset()
            cursor.close()

        return faces, ids

    def __encrypt_and_store(self, face, user):
        """
        Encrypts and stores an image of the user's face in the filesystem

        Performs a symmetric key encryption of an image containing a user face to be used in the face recognition
        process, using AES in CBC mode (once that with ECB the encryption image resembles the original) and PKCS#7
        padding, and then storing the resulting file in an appropriate directory on the filesystem. Other than that,
        it also computes the MAC of the original image for integrity check on the decryption.
        the image's filename.

        :param face: Byte array representing the face to be stored.
        :param user: User id (label) to whom the face belongs to.
        :return: The filename in which the encrypted image was stored and the original image hash digest.
        """

        _dir = self.__data_dir + str(user) + "/"
        if not os.path.exists(_dir):
            os.mkdir(_dir)

        encryptor = self.__cipher.encryptor()
        padder = self.__padder.padder()

        padded_data = padder.update(face) + padder.finalize()
        ciphertext = encryptor.update(padded_data) + encryptor.finalize()

        # hash digest
        h = hmac.HMAC(self.__hash_key, hashes.SHA256(), backend=default_backend())
        h.update(face)
        signature = h.finalize()

        filename = uuid.uuid4().hex
        f = open(_dir + filename, "wb")
        f.write(ciphertext)
        f.close()

        return filename, signature

    def __decrypt_and_verify(self, image, mac, user):
        """
        Decrypts and verifies the integrity of a file on the filesystem containing the face of the user.

        Opens and reads the file, decrypting its data using AES in CBC mode with PKCS#7 padding, verifying if the
        resulting digest matches the one stored when the image was saved, to make sure the file was not tampered with
        for integrity purposes.

        :param image: Filename containing the image to be decrypted.
        :param mac: Message Authentication Code stored in the database to verify the integrity of the file.
        :param user: User id (label) to whom the face belongs to.
        :return: Numpy array representing the decrypted image.
        """

        _dir = self.__data_dir + str(user) + "/"
        if not os.path.exists(_dir):
            return None

        filename = _dir + image
        f = open(filename, "rb")
        image_enc = b"".join(f.readlines())
        f.close()

        # decrypt data
        decryptor = self.__cipher.decryptor()
        unpadder = self.__padder.unpadder()
        padded_data = decryptor.update(image_enc) + decryptor.finalize()
        face = unpadder.update(padded_data) + unpadder.finalize()

        # verify hash digest
        h = hmac.HMAC(self.__hash_key, hashes.SHA256(), backend=default_backend())
        h.update(face)
        try:
            h.verify(mac)
        except cryptography.exceptions.InvalidSignature:
            return None

        return bytes_to_opencv(face)

    def __get_label(self, email):
        """
        Private function to retrieve a user id (used as a label in the LBPHFaceRecognition) from the database, based
        on the user email.

        :param email: email belonging to the user to which will be retrieving the label from
        :return: the user label. Returns None if a connection to the database is not be established.
        """

        if not self.__conn:
            return None
        cursor = self.__conn.cursor()

        query = f"SELECT id FROM USER WHERE email = %s;"
        cursor.execute(query, [email])
        label = cursor.fetchone()
        cursor.close()

        return label[0]

    def user_exists(self, email):
        """
        Verifies if the user already exists on the database, based on their email, by checking if a user with the
        same email already exists (once email is the Primary Key, they have to be unique)

        :param email: Email to verify
        :return: True if the user already exists, False if it does not. Returns None if a connection to the database
        is not established.
        """

        if not self.__conn:
            return None
        cursor = self.__conn.cursor()

        query = f"SELECT email FROM USER WHERE email = %s;"
        cursor.execute(query, [email])
        users = cursor.fetchall()
        cursor.close()

        if len(users) > 0:
            return True
        return False

    def register(self, email, password, collected_images):
        """
        Used to register a user

        Registers a user by first, hashing the provided password, and then inserting it on the database with the user's
        email. After retrieves the created user's id and with that encrypts and stores the faces in the filesystem and
        the corresponding filenames and MACs on the database. After that, updates the LBPHFaceRecognition so that the
        user can be authenticated.

        :param email: Email to register the user with
        :param password: Password to register the user with
        :param collected_images: List of base64 encodings of images from the user face to train the LBPHFaceRecognition
        :return: True if the registration is successful, False otherwise.
        """

        if not self.__conn or self.user_exists(email):
            return False

        cursor = self.__conn.cursor()
        password = hashlib.sha256(password.encode(encoding='utf-8')).hexdigest()
        user_query = "INSERT INTO USER (email, password) VALUES (%s, %s)"
        cursor.execute(user_query, [email, password])
        cursor.reset()

        cursor.execute("SELECT id FROM USER WHERE EMAIL = %s", [email])
        user_id = cursor.fetchone()[0]

        # encrypt and store collected_images and their respective mac
        image_query = "INSERT INTO IMAGE (image, mac, user_id) VALUES (%s, %s, %s)"
        values = [self.__encrypt_and_store(face, user_id) + (user_id, ) for face in collected_images]

        cursor.executemany(image_query, values)
        self.__conn.commit()
        cursor.close()

        self.__recognizer.update(
            [bytes_to_opencv(face) for face in collected_images],
            np.asarray([user_id for _ in collected_images])
        )
        return True

    def authenticate(self, email, image):
        """
        Authenticate a user based on its email and face's image.

        Authenticates a user by first checking if the provided email is registered on the database, if so it retrieves
        the user's id (which will be used as a label for the LBPHFaceRecognition) through the private function
        '__get_labels()'. Afterwards uses the predict method to predict the label and the confidence of the face in
        the image and if the label matches with the user's id retrieved from the database and the confidence is bigger
        or equal to the confidence threshold, then the user is authenticated.

        :param email: email of the user who wants to be authenticated
        :param image: greyscale image of the face of the user who wants to be authenticated
        :return: True if the user is authenticated, False otherwise.
        """

        if not self.__conn or not self.user_exists(email):
            return False
        user_label = self.__get_label(email)

        label, confidence = self.__recognizer.predict(image)
        if label != user_label:
            return False

        if 100-confidence >= self.confidence:
            return True

        return False

    def close(self):
        """
        Closes the database connection, if it is established.
        """

        if self.__conn:
            self.__conn.close()
            print("Connection closed")
