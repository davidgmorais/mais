#!/usr/bin/python3
import os
import time
import PySimpleGUI as sg
from speech_recognition import AudioData
import cv2

MAX_TRIES = 5


class GUI:

    # Initialization function, main window
    def __init__(self, face_detector, face_recognition, voice_authentication):

        self.capture_data = None
        self.face_detector = face_detector
        self.face_recognition = face_recognition
        self.voice_authentication = voice_authentication
        self.register_values = None
        self.authentication_values = None
        self.assets_path = os.path.dirname(os.path.abspath(__file__)) + "/assets/"

        try:
            # Buttons name's
            # ------------------------
            self.registration = "Registration"
            self.authentication = "Authentication"

            # Interface layout
            # ------------------------
            self.layout = [[sg.Text('WHAT DO YOU WANT TO DO ?')],
                           [sg.Button(self.registration), sg.Button(self.authentication)]]

            window = sg.Window("MAIS PROJECT!", self.layout, size=(720, 380), element_justification='center')
            while True:
                event, values = window.read()
                print(event, values)  # Usunąć na końcu tę linijkę
                # Closing window
                if event == sg.WIN_CLOSED or event == 'Exit':
                    break
                if event == self.registration:
                    window.close()
                    GUI.win_registration(self)

                if event == self.authentication:
                    window.close()
                    GUI.win_authentication(self)

        except Exception as err:
            sg.popup(err)
            window.close()

    # Registration window
    # ------------------------
    def win_registration(self):
        try:
            # Interface layout
            # ------------------------
            self.layout = [[sg.Text('REGISTRATION', justification='center')],
                           [sg.Text('Name', size=(15, 1)), sg.InputText(key='name_registration')],
                           [sg.Text('Email', size=(15, 1)), sg.InputText(key='email_registration')],
                           [sg.Text('Password', size=(15, 1)),
                            sg.InputText(password_char="*", key='password_registration')],
                           [sg.Text('Write again password: '), sg.InputText(key='reenter_password', password_char='*')],
                           [sg.Submit(), sg.Cancel()]]
            window = sg.Window("REGISTRATION", self.layout, size=(720, 380), element_justification='center')
            while True:
                event, values = window.read()
                print(event, values)  # Usunąć na końcu tę linijkę
                if event == sg.WIN_CLOSED or event == 'Exit':
                    break
                if event == sg.Submit() or event == 'Submit':
                    self.register_values = values
                    window.close()
                    GUI.win_registration_picture(self)
                if event == sg.Cancel() or event == 'Cancel':
                    window.close()
                    GUI.__init__(self, self.face_detector, self.face_recognition, self.voice_authentication)

        except Exception as err:
            sg.popup()
            window.close()

    # Confiramtion of registration window
    # ------------------------
    def win_registration_conf(self):
        # Interface layout
        # ------------------------
        try:
            self.layout = [[sg.Text('CONFIRMATION', justification='center')],
                           [sg.Button('Ok')], ]
            window = sg.Window("CONFIRMATION", self.layout, size=(720, 380), element_justification='center')
            while True:
                event, values = window.read()
                print(event, values)  # Usunąć na końcu tę linijkę
                if event == sg.WIN_CLOSED or event == 'Exit':
                    break
                if event == sg.Button('Ok') or event == 'Ok':
                    window.close()
                    GUI.win_registration_voice(self)
        except Exception as err:
            sg.popup()
            window.close()

    # Confiramtion of registration window
    # ------------------------
    def win_registration_picture(self):
        # Interface layout
        # ------------------------
        try:
            self.layout = [[sg.Image("", key='picture_registration')],
                           [sg.Button('Close')]]
            window = sg.Window('IMAGE', self.layout, size=(720, 380), element_justification='center')
            self.capture_data = cv2.VideoCapture(0)  # Video capture (frames)
            collected = []

            while True:
                event, values = window.read(timeout=20)
                print(event, values)
                if event == sg.WIN_CLOSED or event == 'Exit':
                    break
                if event == sg.Button('Close') or event == 'Close':
                    if self.capture_data:
                        self.capture_data.release()
                        self.capture_data = None
                    window.close()
                    GUI.win_registration(self)

                if self.capture_data:
                    ret, img = self.capture_data.read()
                    if img is not None:
                        img, roi_gray, _ = self.face_detector.detect(img)
                        height = 240
                        width = int(img.shape[1] / (img.shape[0] / height))
                        img = cv2.resize(img, (width, height), interpolation=cv2.INTER_LINEAR)
                        img_bytes = cv2.imencode(".png", img)[1].tobytes()
                        window['picture_registration'].update(data=img_bytes)

                        if len(roi_gray) != 1:
                            if len(collected) > 0:
                                print("Starting over, make sure you are the only person one in frame")
                                collected = []
                            continue

                        elif len(roi_gray) > 0:
                            roi_bytes = cv2.imencode('.jpg', roi_gray[0])[
                                1].tobytes()  # Numpy one-dim array representative of the img
                            collected.append(roi_bytes)

                            if len(collected) == self.face_recognition.sample_size:
                                print("Collection completing.")
                                print(type(self.register_values), self.register_values)
                                email = self.register_values['email_registration']
                                password = self.register_values['password_registration']
                                print(email, password)
                                if self.face_recognition.register(email, password, collected):
                                    print("User registered with success")
                                    if self.capture_data:
                                        self.capture_data.release()
                                        self.capture_data = None
                                    window.close()
                                    GUI.win_registration_conf(self)

            if self.capture_data:
                self.capture_data.release()
                self.capture_data = None

        except Exception as err:
            sg.popup()
            window.close()

    # ############################################ #
    #               VOICE ENROLLMENT               #
    # ############################################ #

    # voice registration window
    def win_registration_voice(self):
        mic_off_path = self.assets_path + "off.png"
        mic_on_path = self.assets_path + "on.png"

        try:
            self.layout = [[sg.Image(mic_off_path, key='voice_registration', pad=(0, 20))],
                           [sg.Text("The words spoken aren't entirely correct. Try again...", key="warning",
                                    visible=False, text_color=sg.rgb(255, 0, 0))],
                           [sg.Text("", key="message")],
                           [sg.Text("", key="passphrase", font=(None, 15), relief=sg.RELIEF_RAISED)],
                           [sg.Button('Close', key="close_btn"),
                            sg.Button("Continue", visible=False, key="continue_btn")]]
            window = sg.Window('IMAGE', self.layout, size=(720, 380), element_justification='center')
            audio_samples = []
            sample_size = 2
            sample_count = 0
            feedback_ready, passphrase_ready = False, False
            show_warning = False
            sample = None

            _passphrase = self.voice_authentication.generate_passphrase()
            input_str = "Please say the following words"
            suffixes = [":", " again:"]

            while True:
                event, values = window.read(timeout=20)
                print(event, values)

                if event == sg.WIN_CLOSED or event == 'Exit':
                    break
                if event == sg.Button('Close') or event == 'close_btn':
                    window.close()
                    GUI.win_registration(self)
                if event == sg.Button("Continue") or event == "continue_btn":
                    print(audio_samples)
                    email = self.register_values['email_registration']
                    print(email, type(email))
                    if self.voice_authentication.register(self.register_values['email_registration'],
                                                          " ".join(_passphrase), audio_samples):
                        window.close()
                        GUI.win_registration_voice_success(self)
                    else:
                        window.close()
                        GUI.win_registration_voice_error(self)

                # show warning
                if show_warning:
                    window['warning'].update(visible=True)
                else:
                    window['warning'].update(visible=False)

                if sample_count >= sample_size:
                    window["voice_registration"].update(filename=mic_off_path)
                    sample = None
                    show_warning = False
                    window['message'].update("Audio samples obtained successfully")
                    window['close_btn'].update(visible=False)
                    window['passphrase'].update(visible=False)
                    window['continue_btn'].update(visible=True)

                elif not passphrase_ready:
                    window['message'].update(value=input_str + suffixes[sample_count])
                    window['passphrase'].update(value=" ".join(_passphrase))
                    passphrase_ready = True

                elif not sample and not feedback_ready:
                    window["voice_registration"].update(filename=mic_on_path)
                    feedback_ready = True

                elif sample and feedback_ready:
                    window["voice_registration"].update(filename=mic_off_path)
                    feedback_ready = False
                    show_warning = False

                elif sample and not feedback_ready:
                    if self.voice_authentication.validate_passphrase(_passphrase, sample):
                        audio_samples.append(sample)
                        sample = None
                        show_warning = False
                        passphrase_ready = False
                        sample_count += 1
                    else:
                        sample = None
                        show_warning = True

                elif sample_count < sample_size:
                    sample = self.voice_authentication.listen()

        except Exception as err:
            sg.popup(err)
            window.close()

    # voice registration successful window
    def win_registration_voice_success(self):
        # Interface layout
        # ------------------------
        try:
            self.layout = [
                [sg.Text('Voice registration was successful', justification='center', pad=((0, 0), (140, 0)))],
                [sg.Text("Registration is fully completed", justification='center')],
                [sg.Button('Home')]]
            window = sg.Window("Registration successful", self.layout, size=(720, 380), element_justification='center')

            while True:
                event, values = window.read()
                if event == sg.WIN_CLOSED or event == 'Exit':
                    break
                if event == sg.Button('Home') or event == 'Home':
                    window.close()
                    GUI.__init__(self, self.face_detector, self.face_recognition, self.voice_authentication)

        except Exception as err:
            sg.popup(err)
            window.close()

    # voice registration error window
    def win_registration_voice_error(self):
        # Interface layout
        # ------------------------
        try:
            self.layout = [[sg.Text('An error occurred during Voice registration', justification='center',
                                    pad=((0, 0), (140, 0)))],
                           [sg.Text("Please try again", justification='center')],
                           [sg.Button('Home')]]
            window = sg.Window("Error in registration", self.layout, size=(720, 380), element_justification='center')

            while True:
                event, values = window.read()
                if event == sg.WIN_CLOSED or event == 'Exit':
                    break
                if event == sg.Button('Home') or event == 'Home':
                    window.close()
                    GUI.__init__(self, self.face_detector, self.face_recognition, self.voice_authentication)

        except Exception as err:
            sg.popup(err)
            window.close()

    # ############################################ #
    #              FACE AUTHENTICATION             #
    # ############################################ #

    # Authentication window
    # ------------------------
    def win_authentication(self):
        # Interface layout
        # ------------------------
        try:
            self.layout = [[sg.Text('CONFIRMATION', justification='center')],
                           [sg.Text('Email', size=(15, 1)), sg.InputText(key='email_authentication'), sg.Submit()]]
            window = sg.Window("AUTHENTICATION", self.layout, size=(720, 380), element_justification='center')
            while True:
                event, values = window.read()
                print(event, values)  # Usunąć na końcu tę linijkę
                if event == sg.WIN_CLOSED or event == 'Exit':
                    break
                if event == sg.Submit() or event == 'Submit':
                    self.authentication_values = values
                    window.close()
                    GUI.win_authentication_face(self)
        except Exception as err:
            sg.popup()
            window.close()

    # Authentication window
    # ------------------------
    def win_authentication_face(self):
        # Interface layout
        # ------------------------
        tries = 0
        try:
            self.layout = [[sg.Image(key="auth_face")],
                           [sg.Cancel()]]
            window = sg.Window("FACE MAIS", self.layout, size=(720, 380), element_justification='center')
            self.capture_data = cv2.VideoCapture(0)  # Video capture (frames)

            while True:
                event, values = window.read(timeout=20)
                print(event, values)  # Usunąć na końcu tę linijkę
                if event == sg.WIN_CLOSED or event == 'Exit':
                    break

                if event == sg.Cancel() or event == 'Cancel':
                    if self.capture_data:
                        self.capture_data.release()
                        self.capture_data = None
                    window.close()
                    GUI.win_authentication(self)

                if self.capture_data:
                    ret, img = self.capture_data.read()
                    if img is not None:
                        img, roi_gray, _ = self.face_detector.detect(img)
                        height = 240
                        width = int(img.shape[1] / (img.shape[0] / height))
                        img = cv2.resize(img, (width, height), interpolation=cv2.INTER_LINEAR)
                        img_bytes = cv2.imencode(".png", img)[1].tobytes()
                        window['auth_face'].update(data=img_bytes)

                        if len(roi_gray) == 0:
                            continue

                        for roi in roi_gray:
                            if self.face_recognition.authenticate(self.authentication_values['email_authentication'],
                                                                  roi):
                                if self.capture_data:
                                    self.capture_data.release()
                                    self.capture_data = None
                                print("User authenticated, welcome!")
                                window.close()
                                GUI.win_face_authentication_success(self)

                        tries += 1
                        if tries >= MAX_TRIES:
                            if self.capture_data:
                                self.capture_data.release()
                                self.capture_data = None
                            print("\nFace authentication failed.")
                            window.close()
                            GUI.win_authentication_fail(self)

            if self.capture_data:
                self.capture_data.release()
                self.capture_data = None

        except Exception as err:
            sg.popup()
            window.close()

    def win_face_authentication_success(self):
        # Interface layout
        # ------------------------
        try:
            self.layout = [[sg.Text('Face authentication was successful', pad=((0,0), (120,0)), font=(None, 12))],
                           [sg.Text("Click next to start voice authentication")],
                           [sg.Button("Next", key="next_btn")]]
            window = sg.Window("SUCCESSFUL FACE AUTHENTICATION", self.layout, size=(720, 380),
                               element_justification='center')

            while True:
                event, values = window.read()
                if event == sg.WIN_CLOSED or event == 'Exit':
                    break
                if event == sg.Button("Next") or event == "next_btn":
                    window.close()
                    GUI.win_authentication_voice(self)

        except Exception as err:
            sg.popup()
            window.close()

    # ############################################ #
    #             VOICE AUTHENTICATION             #
    # ############################################ #

    # voice authentication window
    def win_authentication_voice(self):
        mic_off_path = self.assets_path + "off.png"
        mic_on_path = self.assets_path + "on.png"

        try:
            self.layout = [[sg.Image(mic_off_path, key='voice_registration', pad=(0, 20))],
                           [sg.Text("The words spoken aren't entirely correct. Try again...", key="warning",
                                    visible=False, text_color=sg.rgb(255, 0, 0))],
                           [sg.Text("Please say the following words", key="message")],
                           [sg.Text("", key="passphrase", font=(None, 15), relief=sg.RELIEF_RAISED)],
                           [sg.Button('Close', key="close_btn")]]
            window = sg.Window('IMAGE', self.layout, size=(720, 380), element_justification='center')
            feedback_ready, passphrase_ready = False, False
            show_warning = False
            sample = None

            _passphrase = self.voice_authentication.get_user_passphrase(
                self.authentication_values['email_authentication'])

            if not _passphrase:
                window.close()
                GUI.win_authentication_fail(self)

            while True:
                event, values = window.read(timeout=20)
                print(event, values)

                if event == sg.WIN_CLOSED or event == 'Exit':
                    break
                if event == sg.Button('Close') or event == 'close_btn':
                    window.close()
                    GUI.win_registration(self)

                # show warning
                if show_warning:
                    window['warning'].update(visible=True)
                else:
                    window['warning'].update(visible=False)

                # display the passphrase
                if not passphrase_ready:
                    window['passphrase'].update(value=" ".join(_passphrase))
                    passphrase_ready = True

                # switch the micro image to the on version
                elif not sample and not feedback_ready:
                    window["voice_registration"].update(filename=mic_on_path)
                    feedback_ready = True

                # switch the micro image to the off version and remove the warning
                elif sample and feedback_ready:
                    window["voice_registration"].update(filename=mic_off_path)
                    feedback_ready = False
                    show_warning = False

                # validate the passphrase
                elif sample and not feedback_ready:
                    if self.voice_authentication.validate_passphrase(_passphrase, sample):
                        show_warning = False
                        passphrase_ready = False

                        # authenticate
                        if self.voice_authentication.authenticate(self.authentication_values['email_authentication'], sample):
                            window.close()
                            GUI.win_authentication_success(self)
                        else:
                            window.close()
                            GUI.win_authentication_fail(self)

                    # passphrase invalid, show warning
                    else:
                        sample = None
                        show_warning = True

                # take an audio sample
                elif not sample and feedback_ready:
                    sample = self.voice_authentication.listen()

        except Exception as err:
            sg.popup(err)
            window.close()

    # Successful confirmation of authentication process window
    # ------------------------
    def win_authentication_success(self):
        # Interface layout
        # ------------------------
        try:
            self.layout = [[sg.Text('SUCCESS! YOU ARE AUTHENTICATED', pad=((0,0), (160,0)))]]
            window = sg.Window("SUCCESSFUL AUTHENTICATION", self.layout, size=(720, 380),
                               element_justification='center')

            while True:
                event, values = window.read()
                if event == sg.WIN_CLOSED or event == 'Exit':
                    break

        except Exception as err:
            sg.popup()
            window.close()

    # Failed to authenticate user
    # ------------------------
    def win_authentication_fail(self):
        # Interface layout
        # ------------------------
        try:
            self.layout = [[sg.Text('FAILED TO AUTHENTICATE USER', pad=((0,0), (160,0)))]]
            window = sg.Window("FAILED TO AUTHENTICATE USER", self.layout, size=(720, 380),
                               element_justification='center')

            while True:
                event, values = window.read()
                if event == sg.WIN_CLOSED or event == 'Exit':
                    break

        except Exception as err:
            sg.popup()
            window.close()

