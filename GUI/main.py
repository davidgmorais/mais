#!/usr/bin/python3
import os
import threading
import PySimpleGUI as sg
import cv2

MAX_TRIES = 5
BLANK_FILED_WARNING = "Field cannot be blank"
EMAIL_USAGE_WARNING = "This email address is already in use"
PASSWORD_MATCH_WARNING = "Passwords don't match"
INVALID_PASSWORD_WARNING = "Password must contain 8 characters"
INVALID_EMAIL_WARNING = "Invalid email address"
IMAGE_COLLECTION_WARNING = "Image collection was interrupted:\n Make sure you are the only person one in frame"


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
        self.collected_images = []

        try:
            # Buttons name's
            # ------------------------
            self.registration = "Registration"
            self.authentication = "Authentication"

            # Interface layout
            # ------------------------
            self.layout = [[sg.Text('WHAT DO YOU WANT TO DO ?', pad=((0, 0), (140, 10)))],
                           [sg.Button(self.registration, pad=10), sg.Button(self.authentication, pad=10)]]

            window = sg.Window("MAIS PROJECT!", self.layout, size=(720, 380), element_justification='center')
            while True:
                event, values = window.read()
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

    # Registration from window
    # ------------------------
    def win_registration(self):
        valid_name, valid_email, valid_password, valid_reenter = False, False, False, False
        try:
            # Interface layout
            # ------------------------
            self.layout = [
                [sg.Text('Please fill in the following form:', justification='center', pad=((0, 0), (20, 30)))],

                [sg.Text('Name', size=(15, 1)), sg.InputText(key='name_registration')],
                [sg.Text("", key="name_warning", pad=((0, 0), (0, 10)), text_color=sg.rgb(255, 0, 0))],

                [sg.Text('Email', size=(15, 1)), sg.InputText(key='email_registration')],
                [sg.Text("", key="email_warning", pad=((0, 0), (0, 10)), text_color=sg.rgb(255, 0, 0))],

                [sg.Text('Password', size=(15, 1)),
                 sg.InputText(password_char="*", key='password_registration')],
                [sg.Text("", key="password_warning", pad=((0, 0), (0, 10)), text_color=sg.rgb(255, 0, 0))],

                [sg.Text('Password again', size=(15, 1)),
                 sg.InputText(key='reenter_password', password_char='*')],
                [sg.Text("", key="matching_warning", pad=((0, 0), (0, 10)), text_color=sg.rgb(255, 0, 0))],

                [sg.Cancel(), sg.Submit()]]
            window = sg.Window("REGISTRATION", self.layout, size=(720, 380), element_justification='center')
            while True:
                event, values = window.read()
                if event == sg.WIN_CLOSED or event == 'Exit':
                    break
                if event == sg.Submit() or event == 'Submit':
                    # name is not blank verification
                    if not values.get("name_registration") or values.get("name_registration") == '':
                        window["name_warning"].update(value=BLANK_FILED_WARNING)
                        valid_name = False
                    else:
                        window["name_warning"].update(value='')
                        valid_name = True

                    # email is not blank verification
                    if not values.get("email_registration") or values.get("email_registration") == '':
                        window["email_warning"].update(value=BLANK_FILED_WARNING)
                        valid_email = False
                    else:
                        values['email_registration'] = values['email_registration'].lower()

                        # invalid email verification:
                        if "@" not in values.get("email_registration") or "." not in \
                                values.get("email_registration").split("@")[-1]:
                            window["email_warning"].update(value=INVALID_EMAIL_WARNING)
                            valid_email = False
                        else:

                            # email already in use verification
                            if self.face_recognition.user_exists(values["email_registration"]):
                                window["email_warning"].update(value=EMAIL_USAGE_WARNING)
                                valid_email = False
                            else:
                                window["email_warning"].update(value='')
                                valid_email = True

                    # password is not blank verification
                    if not values.get("password_registration") or values.get("password_registration") == '':
                        window["password_warning"].update(value=BLANK_FILED_WARNING)
                        valid_password = False
                    else:

                        # invalid password verification
                        if len(values.get("password_registration")) < 8:
                            window["password_warning"].update(value=INVALID_PASSWORD_WARNING)
                            valid_password = False
                        else:
                            window["password_warning"].update(value='')
                            valid_password = True

                    # password again is not blank verification
                    if not values.get("reenter_password") or values.get("reenter_password") == '':
                        window["matching_warning"].update(value=BLANK_FILED_WARNING)
                        valid_reenter = False
                    else:
                        window["matching_warning"].update(value='')

                    # passwords match verification
                    if values.get("password_registration") and values.get("password_registration") != '' and \
                            values.get("reenter_password") and values.get("reenter_password") != '':
                        if values.get("password_registration") != values.get("reenter_password"):
                            window["matching_warning"].update(value=PASSWORD_MATCH_WARNING)
                            valid_reenter = False
                        else:
                            window["matching_warning"].update(value='')
                            valid_reenter = True

                    if valid_name and valid_email and valid_password and valid_reenter:
                        self.register_values = values
                        window.close()
                        GUI.win_registration_picture(self)

                if event == sg.Cancel() or event == 'Cancel':
                    window.close()
                    GUI.__init__(self, self.face_detector, self.face_recognition, self.voice_authentication)

        except Exception as err:
            sg.popup(err)  # nie

    # Confirmation of face collection window
    # ------------------------
    def win_registration_face_conf(self):
        # Interface layout
        # ------------------------
        try:
            if self.register_values and self.register_values.get("email_registration") and \
                    self.register_values.get("password_registration") and self.collected_images and \
                    len(self.collected_images) == self.face_recognition.sample_size:

                self.layout = [[sg.Image(self.assets_path + "success.png", pad=((0, 0), (80, 0)))],
                               [sg.Text('Image collection was successful', pad=((0, 0), (20, 0)), font=(None, 12))],
                               [sg.Text("Click next to start voice registration", pad=((0, 0), (0, 20)))],
                               [sg.Button("Next", key="next_btn")]]
            else:
                self.layout = [[sg.Image(self.assets_path + "error.png", pad=((0, 0), (80, 0)))],
                               [sg.Text('Something went wrong.', pad=((0, 0), (20, 0)), font=(None, 12))],
                               [sg.Text("Click Cancel to go to back the home page and try again", pad=((0, 0), (0, 20)))],
                               [sg.Cancel()]]

            window = sg.Window("FACE COLLECTION COMPLETED", self.layout, size=(720, 380),
                               element_justification='center')
            while True:
                event, values = window.read()

                if event == sg.WIN_CLOSED or event == 'Exit':
                    break
                if event == sg.Cancel() or event == 'Cancel':
                    window.close()
                    GUI.__init__(self, self.face_detector, self.face_recognition, self.voice_authentication)
                if event == sg.Button('Next') or event == 'next_btn':
                    window.close()
                    GUI.win_registration_voice(self)

        except Exception as err:
            sg.popup(err)  # nie

    # Image collection for registration window
    # ------------------------
    def win_registration_picture(self):
        # Interface layout
        # ------------------------
        try:
            self.layout = [[sg.Text("Please, look into the camera")],
                           [sg.Image("", key='picture_registration')],
                           [sg.Text("\n", key="image_collection_warning", text_color=sg.rgb(255, 0, 0),
                                    justification="center")],
                           [sg.Button('Close')]]
            window = sg.Window('IMAGE', self.layout, size=(720, 380), element_justification='center')
            self.capture_data = cv2.VideoCapture(0)  # Video capture (frames)
            collected = []

            while True:
                event, values = window.read(timeout=20)
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
                                window["image_collection_warning"].update(value=IMAGE_COLLECTION_WARNING)
                                print("Starting over, make sure you are the only person one in frame")
                                collected = []
                            continue

                        elif len(roi_gray) > 0:
                            roi_bytes = cv2.imencode('.jpg', roi_gray[0])[
                                1].tobytes()  # Numpy one-dim array representative of the img
                            collected.append(roi_bytes)

                            if len(collected) == self.face_recognition.sample_size:
                                print("Collection completing.")
                                self.collected_images = collected
                                if self.capture_data:
                                    self.capture_data.release()
                                    self.capture_data = None
                                window.close()
                                GUI.win_registration_face_conf(self)
                        window["image_collection_warning"].update(value="\n")

            if self.capture_data:
                self.capture_data.release()
                self.capture_data = None

        except Exception as err:
            sg.popup(err)  # nie

    # ############################################ #
    #               VOICE ENROLLMENT               #
    # ############################################ #
    def gui_listener_wrapper(self, window):
        print("Starting listening")
        sample = self.voice_authentication.listen()
        try:
            window.write_event_value("SAMPLE COLLECTED", sample)
        except Exception:
            return
        return

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
            pid = None

            _passphrase = self.voice_authentication.generate_passphrase()
            input_str = "Please say the following words"
            suffixes = [":", " again:"]

            while True:
                event, values = window.read(timeout=20)
                if event == sg.WIN_CLOSED or event == 'Exit':
                    break
                if event == sg.Button('Close') or event == 'close_btn':
                    window.close()
                    GUI.win_registration(self)
                if event == sg.Button("Continue") or event == "continue_btn":

                    if self.register_values and self.register_values.get("email_registration") and \
                            self.register_values.get("password_registration") and self.collected_images and \
                            len(self.collected_images) == self.face_recognition.sample_size and \
                            len(audio_samples) == sample_size:

                        # registration process
                        email = self.register_values['email_registration']
                        password = self.register_values["password_registration"]

                        if self.face_recognition.register(email, password, self.collected_images):
                            print("User registered with success in face recognition module")
                        else:
                            window.close()
                            GUI.win_registration_error(self)

                        if self.voice_authentication.register(email, " ".join(_passphrase), audio_samples):
                            print("User registered with success in voice recognition module")
                            window.close()
                            GUI.win_registration_voice_success(self)
                        else:
                            self.face_recognition.remove_user(email)
                            window.close()
                            GUI.win_registration_error(self)

                    else:
                        window.close()
                        GUI.win_registration_error(self)

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
                    self.voice_authentication.adjust_for_ambient()
                    window["voice_registration"].update(filename=mic_on_path)
                    feedback_ready = True

                elif sample and feedback_ready:
                    window["voice_registration"].update(filename=mic_off_path)
                    feedback_ready = False
                    show_warning = False

                elif sample and not feedback_ready:
                    if self.voice_authentication.validate_passphrase(_passphrase, sample):
                        audio_samples.append(sample)
                        show_warning = False
                        passphrase_ready = False
                        sample_count += 1
                    else:
                        show_warning = True
                    sample = None
                    pid = None

                elif sample_count < sample_size and not pid:
                    pid = threading.Thread(
                        target=self.gui_listener_wrapper,
                        args=(window,),
                        daemon=True
                    )
                    pid.start()
                    # sample = self.voice_authentication.listen()

                elif event == "SAMPLE COLLECTED":
                    sample = values["SAMPLE COLLECTED"]

        except Exception as err:
            sg.popup(err)

    # voice registration successful window
    def win_registration_voice_success(self):
        # Interface layout
        # ------------------------
        try:
            self.layout = [
                [sg.Image(self.assets_path + "success.png", pad=((0, 0), (90, 0)))],
                [sg.Text('Voice registration was successful', justification='center', pad=((0, 0), (20, 0)))],
                [sg.Text("Registration is fully completed", justification='center')],
                [sg.Button('Home', pad=(0, 5))]]
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

    # voice registration error window
    def win_registration_error(self):
        # Interface layout
        # ------------------------
        try:
            self.layout = [
                [sg.Image(self.assets_path + "error.png", pad=((0, 0), (90, 0)))],
                [sg.Text('An error occurred during the registration process', justification='center', pad=((0, 0), (20, 0)))],
                [sg.Text("Please try again", justification='center')],
                [sg.Button('Home', pad=(0, 5))]]
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

    # ############################################ #
    #              FACE AUTHENTICATION             #
    # ############################################ #

    # Authentication window
    # ------------------------
    def win_authentication(self):
        # Interface layout
        # ------------------------
        try:
            self.layout = [[sg.Text('Please, introduce your email so we can start.', justification='center',
                                    pad=((0, 0), (120, 10)))],
                           [sg.Text('Email', size=(8, 1)), sg.InputText(key='email_authentication')],
                           [sg.Text("", key="email_warning", pad=((0, 0), (0, 10)), text_color=sg.rgb(255, 0, 0))],
                           [sg.Cancel(pad=(5, 10)), sg.Submit(pad=(5, 10))]]
            window = sg.Window("AUTHENTICATION", self.layout, size=(720, 380), element_justification='center')
            while True:
                event, values = window.read()
                if event == sg.WIN_CLOSED or event == 'Exit':
                    break

                if event == sg.Submit() or event == 'Submit':
                    # email is not blank verification
                    if not values.get("email_authentication") or values.get("email_authentication") == '':
                        window["email_warning"].update(value=BLANK_FILED_WARNING)
                    else:
                        values['email_authentication'] = values['email_authentication'].lower()

                        # invalid email verification:
                        if "@" not in values.get("email_authentication") or "." not in \
                                values.get("email_authentication").split("@")[-1]:
                            window["email_warning"].update(value=INVALID_EMAIL_WARNING)
                        else:
                            window["email_warning"].update(value="")
                            self.authentication_values = values
                            window.close()
                            GUI.win_authentication_face(self)

                elif event == sg.Cancel() or event == 'Cancel':
                    window.close()
                    GUI.__init__(self, self.face_detector, self.face_recognition, self.voice_authentication)

        except Exception as err:
            sg.popup(err)

    # Authentication window
    # ------------------------
    def win_authentication_face(self):
        # Interface layout
        # ------------------------
        tries = 0
        sleep = 15  # so that the first frame is not grabbed immediately and the info can be displayed
        try:
            self.layout = [[sg.Text("Please, look into the camera")],
                           [sg.Image("", key='auth_face')],
                           [sg.Cancel()]]

            window = sg.Window("FACE MAIS", self.layout, size=(720, 380), element_justification='center')
            self.capture_data = cv2.VideoCapture(0)  # Video capture (frames)

            while True:
                event, values = window.read(timeout=20)
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

                        if sleep > 0:
                            sleep -= 1
                            continue

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
            sg.popup(err)

    def win_face_authentication_success(self):
        # Interface layout
        # ------------------------
        try:
            self.layout = [[sg.Image(self.assets_path + "success.png", pad=((0, 0), (90, 0)))],
                           [sg.Text('Face authentication was successful', pad=((0, 0), (20, 0)), font=(None, 12))],
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
            sg.popup(err)

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
                           [sg.Cancel()]]
            window = sg.Window('IMAGE', self.layout, size=(720, 380), element_justification='center')
            feedback_ready, passphrase_ready = False, False
            show_warning = False
            sample = None
            pid = None

            _passphrase = self.voice_authentication.get_user_passphrase(
                self.authentication_values['email_authentication'])

            if not _passphrase:
                window.close()
                GUI.win_authentication_fail(self)

            while True:
                event, values = window.read(timeout=20)

                if event == sg.WIN_CLOSED or event == 'Exit':
                    break
                if event == sg.Cancel() or event == 'Cancel':
                    window.close()
                    GUI.win_authentication(self)

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
                    self.voice_authentication.adjust_for_ambient()
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
                        if self.voice_authentication.authenticate(self.authentication_values['email_authentication'],
                                                                  sample):
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
                elif not sample and feedback_ready and not pid:
                    pid = threading.Thread(
                        target=self.gui_listener_wrapper,
                        args=(window,),
                        daemon=True
                    )
                    pid.start()
                    # sample = self.voice_authentication.listen()

                elif event == "SAMPLE COLLECTED":
                    sample = values["SAMPLE COLLECTED"]

        except Exception as err:
            sg.popup(err)

    # Successful confirmation of authentication process window
    # ------------------------
    def win_authentication_success(self):
        # Interface layout
        # ------------------------
        try:
            self.layout = [[sg.Image(self.assets_path + "success.png", pad=((0, 0), (100, 0)))],
                           [sg.Text('SUCCESS! YOU ARE AUTHENTICATED', pad=((0, 0), (20, 10)))],
                           [sg.Button("Home")]]
            window = sg.Window("SUCCESSFUL AUTHENTICATION", self.layout, size=(720, 380),
                               element_justification='center')

            while True:
                event, values = window.read()
                if event == sg.WIN_CLOSED or event == 'Exit':
                    break

                if event == sg.Button("Home") or event == "Home":
                    window.close()
                    GUI.__init__(self, self.face_detector, self.face_recognition, self.voice_authentication)

        except Exception as err:
            sg.popup(err)

    # Failed to authenticate user
    # ------------------------
    def win_authentication_fail(self):
        # Interface layout
        # ------------------------
        try:
            self.layout = [[sg.Image(self.assets_path + "error.png", pad=((0, 0), (100, 0)))],
                           [sg.Text('FAILED TO AUTHENTICATE USER', pad=((0, 0), (20, 10)))],
                           [sg.Button("Home")]]
            window = sg.Window("FAILED TO AUTHENTICATE USER", self.layout, size=(720, 380),
                               element_justification='center')

            while True:
                event, values = window.read()
                if event == sg.WIN_CLOSED or event == 'Exit':
                    break

                if event == sg.Button("Home") or event == "Home":
                    window.close()
                    GUI.__init__(self, self.face_detector, self.face_recognition, self.voice_authentication)

        except Exception as err:
            sg.popup(err)
