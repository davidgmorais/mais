import os
import shutil
import uuid
import cryptography.exceptions
import numpy as np
import speech_recognition
from random_words import RandomWords
from speech_recognition import Recognizer, Microphone
from scipy.io.wavfile import read
from python_speech_features import mfcc, delta
from sklearn import preprocessing
from sklearn.mixture import GaussianMixture
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding, hmac, hashes
from cryptography.hazmat.backends import default_backend
from database.database_manager import DatabaseManager


class VoiceAuthentication:
    def __init__(self, database, confidence=0.0):
        self.__recognizer = None
        self.__db = database
        self.log_likelihood_threshold = confidence - 100
        self.N = 2  # used for delta calculations in feature extraction
        self.passphrase_length = 2

        # directory to save encrypted data
        self.__wav_dir = "data/"
        if not os.path.exists(self.__wav_dir):
            os.mkdir(self.__wav_dir)
        self.__wav_dir += "wav/"
        if not os.path.exists(self.__wav_dir):
            os.mkdir(self.__wav_dir)

        # keys for encryption and decryption
        self.__key = b'\x8d\x16\xd2cV\x88\xca\xfe\x7f\xca\xc6\xf3\x8b\x9d\xa1\x86'
        self.__iv = b'\x14\x07\xb5b\x02.\xbd\x9f\x8f\x0b \xad\x1ddS\xec'
        self.__hash_key = b'(\xa4\xb2\xf5V\x9b\x86\x1e\xfb\xcd\xb8\xc7\xcd\x1c\xafw'

        # initialize AES cipher in CBC mode with PKCS7 padder
        self.__cipher = Cipher(algorithms.AES(self.__key), modes.CBC(self.__iv), default_backend())
        self.__padder = padding.PKCS7(algorithms.AES.block_size)

        if not self.__db:
            return

        self.__model_collection = dict()
        # preload the model based on the users already on the system
        wav_list = self.__get_wav_file_list_by_users()

        for _user in wav_list.keys():
            if len(wav_list[_user]) > 0:
                self.__update_model_collection(wav_list[_user], _user)

    def __get_wav_file_list_by_users(self):
        """
        Private function to list all the pairs (filename, signature) of the voice samples of all users in the database

        :return: a dictionary, where the key is the user_id and the value is a list of tuples (filename, signature)
        """
        wav_list = dict()
        if self.__db:
            users = self.__db.get_users()
            for user in users:
                wav_list[user] = self.__db.get_wavs_by_user(user)

        return wav_list

    def __encrypt_and_store(self, audio, user):
        """
        Encrypts and stores a .wav file of the user's voice in the filesystem

        Performs a symmetric key encryption of a .wav audio file containing a user's voice to be used in the voice
        authentication process, using AES in CBC mode and PKCS#7 padding, and then storing the resulting file in an
        appropriate directory on the filesystem. Furthermore, it also computes the MAC of the original file for
        integrity check on the decryption.

        :param audio: audio file to be store
        :param user: user id to whom the voice belongs to
        :return: The encrypted data's filename and the original audio sample hash digest.
        """

        _dir = self.__wav_dir + str(user) + "/"
        if not os.path.exists(_dir):
            os.mkdir(_dir)

        encryptor = self.__cipher.encryptor()
        padder = self.__padder.padder()

        padded_data = padder.update(audio.get_wav_data()) + padder.finalize()
        ciphertext = encryptor.update(padded_data) + encryptor.finalize()

        # hash digest
        h = hmac.HMAC(self.__hash_key, hashes.SHA256(), backend=default_backend())
        h.update(audio.get_wav_data())
        signature = h.finalize()

        filename = uuid.uuid4().hex
        f = open(_dir + filename, "wb")
        f.write(ciphertext)
        f.close()

        return filename, signature

    def __decrypt_and_verify(self, voice, mac, user):
        """
        Decrypts and verifies the integrity of a file on the filesystem containing an audio sample of the user.

        Opens and reads the file, decrypting its data using AES in CBC mode with PKCS#7 padding, verifying if the
        resulting digest matches the one stored when the audio file was saved, to make sure the file was not tampered
        with for integrity purposes, and store the audio sample in a temporary directory.

        :param voice: filename containing the encrypted audio data
        :param mac: Message Authentication Code stored in the database to verify the integrity of the file.
        :param user: User id to whom the voice belongs to.
        :return: filename of the temporary file
        """

        _dir = self.__wav_dir + str(user) + "/"
        if not os.path.exists(_dir):
            return None
        _tmp_dir = self.__wav_dir + ".tmp/"
        if not os.path.exists(_tmp_dir):
            os.mkdir(_tmp_dir)

        filename = _dir + voice
        f = open(filename, "rb")
        voice_enc = b"".join(f.readlines())
        f.close()

        decryptor = self.__cipher.decryptor()
        unpadder = self.__padder.unpadder()
        padded_data = decryptor.update(voice_enc) + decryptor.finalize()
        voice = unpadder.update(padded_data) + unpadder.finalize()

        # verify the digest
        h = hmac.HMAC(self.__hash_key, hashes.SHA256(), backend=default_backend())
        h.update(voice)
        try:
            h.verify(mac)
        except cryptography.exceptions.InvalidSignature:
            return None

        # store to temp file
        filename = uuid.uuid4().hex + "_tmp.wav"
        with open(_tmp_dir + filename, "wb") as tmp_file:
            tmp_file.write(voice)

        return filename

    def __update_model_collection(self, filenames, user):
        """
        Private function used to update the collection of Gaussian Mixture models used to perform voice authentication.

        For every tuple (filename, signature) passed in the array filenames, the file is decrypted, verified (with the
        signature) and then stored in a tmp folder. Afterwards, the audio and audio rate are read from the temporary
        file and the features are extracted to be used to train a model, stacked onto the features tuple, and the
        temporary file is then deleted.
        With all the features ready, we use train a GaussianMixture model using the tuple of features, and put it in
        the model collection dictionary, with the key being the user id.

        :param filenames: list of tuples (filename, signature) of audio files belonging to the same user to use to
        train a new GaussianMixture model.
        :param user: user id to whom the audio samples belong to.
        """

        _tmp_dir = self.__wav_dir + ".tmp/"
        if not os.path.exists(_tmp_dir):
            os.mkdir(_tmp_dir)
        features = np.array([])

        for filename, signature in filenames:

            tmp_filename = self.__decrypt_and_verify(filename, signature, user)

            rate, audio = read(_tmp_dir + tmp_filename)
            extracted = self.__extract_features(rate, audio)

            if features.size == 0:
                features = extracted
            else:
                features = np.vstack((features, extracted))

            # remove tmp file
            if os.path.exists(_tmp_dir + tmp_filename):
                os.remove(_tmp_dir + tmp_filename)

        gmm = GaussianMixture(n_components=16, max_iter=200, covariance_type='diag', n_init=3)
        gmm.fit(features)
        print("[LOG] Modeling complete")
        self.__model_collection[user] = gmm

    def __extract_features(self, rate, audio):
        """
        Private function to extract feature from and audio sample.

        Compute mfcc features from an audio sample, as well as the delta features of those mfcc features, and combining
        them both in order to generate the final feature vector.

        :param rate: rate of the audio sample.
        :param audio: audio sample.
        :return: feature vector combining the mfcc features and the delta features.
        """

        _mfcc = mfcc(audio, rate, winlen=0.05, winstep=0.01, numcep=5, nfilt=30,
                     nfft=2205, appendEnergy=True)
        _mfcc = preprocessing.scale(_mfcc)
        _delta = delta(_mfcc, self.N)

        # combine mfcc with delta
        return np.hstack((_mfcc, _delta))

    def generate_passphrase(self):
        """
        Generates a passphrase of passphrase_length length to be used in the text dependent voice authentication.

        :return: list of random words.
        """
        return RandomWords().random_words(count=self.passphrase_length)

    def validate_passphrase(self, passphrase, audio):
        """
        Validates the passphrase, given an audio sample, using google speech recognition.

        :param passphrase: passphrase used a prompt.
        :param audio: audio sample from where to recognize words spoken and validate it against the passphrase param.
        :return: True if the recognized words match the passphrase, False otherwise.
        """
        if not self.__recognizer:
            self.__recognizer = Recognizer()

        if not isinstance(audio, speech_recognition.AudioData):
            return False

        try:
            recognized_passphrase = self.__recognizer.recognize_google(audio)
        except speech_recognition.UnknownValueError:
            return False

        recognized_passphrase = recognized_passphrase.lower()
        print("[LOG] Recognized passphrase:", recognized_passphrase)
        print(passphrase)
        if recognized_passphrase.split(" ") == passphrase:
            return True
        return False

    def get_user_passphrase(self, email):
        """
        Retrieves the passphrase of a registered user from the database to be used in the authentication phase.

        :param email: user email.
        :return: List of the passphrase words.
        """

        if not self.__db:
            return None

        return self.__db.get_user_passphrase_by_email(email)

    def adjust_for_ambient(self):
        """
        Function used to adjust the recognizer to ambient noises.
        """
        self.__recognizer = Recognizer()
        mic = Microphone()
        with mic as source:
            self.__recognizer.adjust_for_ambient_noise(source, duration=0.8)
            print("[LOG] Adjustments made.")

    def listen(self):
        """
        Function used to obtain an audio sample from the microphone.

        :return: audio sample obtained form the mic.
        """
        if not self.__recognizer:
            self.__recognizer = Recognizer()
        mic = Microphone()

        with mic as source:
            try:
                audio = self.__recognizer.listen(source, timeout=3, phrase_time_limit=3)
            except speech_recognition.WaitTimeoutError:
                print("[LOG] TIMEOUT: Forced finished listening")
                return None
            print("[LOG] Finished listening.")

        return audio

    def user_exists(self, email):
        """
        Verifies if the user already exists on the database, based on their email, by checking if a user with the
        same email already exists (once email is the Primary Key, they have to be unique)

        :param email: Email to verify
        :return: True if the user already exists, False if it does not. Returns None if a connection to the database
        is not established.
        """
        if not self.__db:
            return None

        return self.__db.user_exists_by_email(email)

    def register(self, email, passphrase, audio_samples):
        """
        Used to register a user.

        Retrieves the user's id and with that encrypts and stores the audio samples in the filesystem and the
        corresponding filenames and MACs on the database. After that, adds the passphrase to the user's entry on the
        database and updates the GaussianMixture model collection so that the user can be authenticated.

        :param email: user email.
        :param passphrase: passphrase used to prompt the audio samples.
        :param audio_samples: list of audio samples to be used in the enrollment phase.
        :return: True if the operation was successful, False otherwise.
        """

        if not self.__db or not self.user_exists(email):
            return False

        user_id = self.__db.get_user_id_by_email(email)
        self.__db.update_user_passphrase_by_user_id(passphrase, user_id)

        # encrypt and store
        samples = [self.__encrypt_and_store(audio, user_id) for audio in audio_samples]
        if not self.__db.add_waves([_sample + (user_id,) for _sample in samples]):
            # remove wav
            _dir = self.__wav_dir + str(user_id) + "/"
            shutil.rmtree(_dir)
            return False

        self.__update_model_collection(samples, user_id)
        return True

    def authenticate(self, email, audio):
        """
        Authenticate a user based on its email and audio sample

        Authenticates a user by first checking if the provided email is registered on the database, if so it retrieves
        the user's id and storing the audio sample in a temporary file. Using that file, the features are extracted and
        the model is selected from the models collection based on the user id retrieved and, afterwards, the feature are
        compared to the selected model and the log likelihood is computed. if this likelihood is above a threshold
        (log_likelihood_threshold) then the user is successfully authenticated.

        :param email: user's email
        :param audio: audio source used to authenticate the user.
        :return: True if the user was authenticated with success, False otherwise.
        """

        if not self.__db:
            return None
        _dir = self.__wav_dir + ".tmp/"
        if not os.path.exists(_dir):
            os.mkdir(_dir)

        user_id = self.__db.get_user_id_by_email(email)

        filename = uuid.uuid4().hex + ".wav"
        with open(_dir + filename, "wb") as audiofile:
            audiofile.write(audio.get_wav_data())

        rate, audio = read(_dir + "/" + filename)
        extracted = self.__extract_features(rate, audio)

        gmm = self.__model_collection[user_id]

        scores = np.array(gmm.score(extracted))
        log_likelihood = scores.sum()

        print("Likelihood:", log_likelihood)
        if log_likelihood > self.log_likelihood_threshold:
            os.remove(_dir + "/" + filename)
            self.__db.log_record(user_id, 'Voice ID', True)
            return True

        os.remove(_dir + "/" + filename)
        self.__db.log_record(user_id, 'Voice ID', False)
        return False

    def get_records(self):
        # TODO: add admin verifications ?
        records = self.__db.get_records("Voice ID")
        return records


if __name__ == "__main__":
    debug = "auth"
    db = DatabaseManager()
    voice_auth = VoiceAuthentication(db, confidence=95)

    # ========================================================== #
    #                   Registration main                        #
    # ========================================================== #
    if debug == "enroll":
        sample_size = 2
        sample_count = 0

        _email = input("Email:")

        input_str = "Please say the following words"
        suffixes = [":\n", " again:\n", " one last time:\n"]
        _audio_samples = [None] * sample_size
        _passphrase = voice_auth.generate_passphrase()

        print("Passphrase is:", _passphrase)

        for sample_count in range(sample_size):
            while _audio_samples[sample_count] is None:
                print(input_str + suffixes[sample_count] + " ".join(_passphrase))
                sample = voice_auth.listen()
                if voice_auth.validate_passphrase(_passphrase, sample):
                    _audio_samples[sample_count] = sample
                else:
                    print("The words spoken aren't entirely correct. Please try again...")
                    print("\n\n")

        voice_auth.register(_email, " ".join(_passphrase), _audio_samples)

    # ========================================================== #
    #                 Authentication main                        #
    # ========================================================== #
    if debug == "auth":
        input_str = "Please say the passphrase:\n"

        _email = input("Email: ")

        _passphrase = voice_auth.get_user_passphrase(_email)  # voice_auth.generate_passphrase()
        if not _passphrase:
            print("Failed Authentication!")
            exit(0)

        print(input_str + " ".join(_passphrase))
        sample = voice_auth.listen()
        while not voice_auth.validate_passphrase(_passphrase, sample):
            print("The words spoken aren't entirely correct. Please try again...")
            print(input_str + " ".join(_passphrase))
            sample = voice_auth.listen()

        if voice_auth.authenticate(_email, sample):
            print("User authenticated, welcome!")
        else:
            print("Failed Authentication")
