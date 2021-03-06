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
        self.dashboard_redirect = False

        try:
            # Buttons name's
            # ------------------------
            self.registration = "Registration"
            self.authentication = "Authentication"

            # Interface layout
            # ------------------------
            self.layout = [[sg.Text('WHAT DO YOU WANT TO DO ?', pad=((0, 0), (140, 10)))],
                           [sg.Button(self.registration, pad=10), sg.Button(self.authentication, pad=10)],
                           [sg.Text("Admin Dashboard", enable_events=True, key="dashboard", font=(None, 9, 'underline'),
                                    pad=((0, 0), (100, 0)))]]

            window = sg.Window("MAIS PROJECT!", self.layout, size=(720, 380), element_justification='center')
            while True:
                event, values = window.read()
                # Closing window
                if event == sg.WIN_CLOSED or event == 'Exit':
                    break
                if event == self.registration:
                    window.close()
                    GUI.win_registration(self)

                elif event == self.authentication:
                    window.close()
                    GUI.win_authentication(self)

                elif event == "dashboard":
                    self.dashboard_redirect = True
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
                               [sg.Text("Click Cancel to go to back the home page and try again",
                                        pad=((0, 0), (0, 20)))],
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
        if window:
            try:
                window.write_event_value("SAMPLE COLLECTED", sample)
            except Exception:
                return
        return

    # voice registration window
    def win_registration_voice(self):
        mic_off_path = self.assets_path + "off.png"
        mic_on_path = self.assets_path + "on.png"
        reload_path = self.assets_path + "reload.png"

        try:
            self.layout = [[sg.Image(mic_off_path, key='voice_registration', pad=(0, 20))],
                           [sg.Text("The words spoken aren't entirely correct. Try again...", key="warning",
                                    visible=False, text_color=sg.rgb(255, 0, 0))],
                           [sg.Text("", key="message")],
                           [sg.Text("", key="passphrase", font=(None, 15), relief=sg.RELIEF_RAISED)],
                           [sg.Button('Close', key="close_btn"),
                            sg.Button(image_filename=reload_path, key="regen_pass",
                                      tooltip="Are these words too hard for you? Generate a new passphrase"),
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
                    break
                if event == "regen_pass":
                    restart = sg.popup_ok_cancel(
                        "Are you sure you want to generate a new passphrase?",
                        "All the progress you've done in the voice enrollment will be erased and will have to be restarted",
                        title="Generate a new passphrase?",
                        keep_on_top=True
                    )
                    if restart == "OK":
                        window.close()
                        GUI.win_registration_voice(self)
                        break

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
                            break

                        if self.voice_authentication.register(email, " ".join(_passphrase), audio_samples):
                            print("User registered with success in voice recognition module")
                            window.close()
                            GUI.win_registration_voice_success(self)
                            break
                        else:
                            self.face_recognition.remove_user(email)
                            window.close()
                            GUI.win_registration_error(self)
                            break

                    else:
                        window.close()
                        GUI.win_registration_error(self)
                        break

                # show warning
                if show_warning:
                    window['warning'].update(visible=True)
                else:
                    window['warning'].update(visible=False)

                if sample_count >= sample_size:
                    try:
                        window["voice_registration"].update(filename=mic_off_path)
                        sample = None
                        show_warning = False
                        window['message'].update("Audio samples obtained successfully")
                        window['close_btn'].update(visible=False)
                        window['regen_pass'].update(visible=False)
                        window['passphrase'].update(visible=False)
                        window['continue_btn'].update(visible=True)
                    except Exception:
                        sample = None
                        show_warning = False

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
                    if not values["SAMPLE COLLECTED"]:
                        show_warning = True
                        sample = TimeoutError
                    else:
                        show_warning = False
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
                [sg.Text('An error occurred during the registration process', justification='center',
                         pad=((0, 0), (20, 0)))],
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
                            print("Face authentication failed.")
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
                           [sg.Text("", key="warning",
                                    visible=False, text_color=sg.rgb(255, 0, 0))],
                           [sg.Text("Please say the following words", key="message")],
                           [sg.Text("", key="passphrase", font=(None, 15), relief=sg.RELIEF_RAISED)],
                           [sg.Cancel()]]
            window = sg.Window('IMAGE', self.layout, size=(720, 380), element_justification='center')
            feedback_ready, passphrase_ready = False, False
            show_warning = None
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
                    break

                # show warning
                if show_warning:
                    window['warning'].update(visible=True)
                    window['warning'].update(value=show_warning)
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
                    if show_warning == "You can speak now, red mic says go!":
                        sample = None
                        pid = None

                # validate the passphrase
                elif sample and not feedback_ready:
                    pid = None
                    if self.voice_authentication.validate_passphrase(_passphrase, sample):

                        # authenticate
                        if self.voice_authentication.authenticate(self.authentication_values['email_authentication'],
                                                                  sample):
                            window.close()
                            GUI.win_authentication_success(self)
                            break
                        else:
                            window.close()
                            GUI.win_authentication_fail(self)
                            break

                    # passphrase invalid, show warning
                    else:
                        sample = None
                        show_warning = "The words spoken aren't entirely correct. Try again..."

                # take an audio sample
                elif not sample and feedback_ready and not pid:
                    pid = threading.Thread(
                        target=self.gui_listener_wrapper,
                        args=(window,),
                        daemon=True
                    )
                    pid.start()

                elif event == "SAMPLE COLLECTED":
                    if window and values:
                        if not values["SAMPLE COLLECTED"]:
                            show_warning = "You can speak now, red mic says go!"
                            sample = TimeoutError
                        else:
                            show_warning = None
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
                           [sg.Button("Proceed to dashboard", key="dash") if self.dashboard_redirect else sg.Button("Home")]]
            window = sg.Window("SUCCESSFUL AUTHENTICATION", self.layout, size=(720, 380),
                               element_justification='center')

            while True:
                event, values = window.read()
                if event == sg.WIN_CLOSED or event == 'Exit':
                    break

                if event == sg.Button("Home") or event == "Home":
                    window.close()
                    GUI.__init__(self, self.face_detector, self.face_recognition, self.voice_authentication)
                elif event == "dash":
                    window.close()
                    GUI.win_dashboard(self)

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

    # ############################################ #
    #                  DASHBOARD                   #
    # ############################################ #
    def win_dashboard(self):
        justification = None
        _email = self.authentication_values['email_authentication']
        if self.face_recognition.is_admin(_email) and self.voice_authentication.is_admin(_email):
            sort_types = ["Sort", ['By latest', 'By oldest', 'By email']]
            filter_types = ["Filter", ["All", "Succeeded", "Failed", "Face ID", "Voice ID"]]

            _face_records = self.face_recognition.get_records()
            _face_success_count = len([rec for rec in _face_records if rec[2] == "SUCCEEDED"])
            _face_auth_rate = (_face_success_count * 100 / len(_face_records)) if len(_face_records) > 0 else 0.0

            _voice_records = self.voice_authentication.get_records()
            _voice_success_count = len([rec for rec in _voice_records if rec[2] == "SUCCEEDED"])
            _voice_auth_rate = _voice_success_count * 100 / len(_voice_records) if len(_voice_records) > 0 else 0.0

            data = sorted(_face_records + _voice_records, key=lambda row: row[1], reverse=True)
            _mais_auth_rate = (_face_success_count + _voice_success_count) * 100 / len(data) if len(data) > 0 else 0.0

            self.layout = [
                [[sg.Text('DASHBOARD', font=(None, 18), pad=((0, 500), (0, 0))),
                  sg.Button(image_filename=self.assets_path + "logout.png", tooltip="Exit", key="exit")]],

                [[sg.Text("Total users:"), sg.Text(self.face_recognition.get_user_count(), key="total_users")],
                 [sg.HorizontalSeparator(pad=((0, 0), (0, 10)))],

                 [sg.Text("Face Auth rate:"),
                  sg.Text('{0:.2f}'.format(_face_auth_rate) + "%", pad=((0, 70), (0, 0)), key="face_auth_rate",
                          text_color=sg.rgb(34, 178,
                                            34) if _face_auth_rate > self.face_recognition.confidence else sg.rgb(178,
                                                                                                                  34,
                                                                                                                  34)),
                  sg.Text("Voice Auth rate:"),
                  sg.Text('{0:.2f}'.format(_voice_auth_rate) + "%", pad=((0, 70), (0, 0)), key="voice_auth_rate",
                          text_color=sg.rgb(34, 178,
                                            34) if _voice_auth_rate > self.voice_authentication.log_likelihood_threshold + 100 else sg.rgb(
                              178, 34, 34)),
                  sg.Text("MAIS auth rate:"),
                  sg.Text('{0:.2f}'.format(_mais_auth_rate) + "%", pad=((0, 70), (0, 0)), key="auth_rate",
                          text_color=sg.rgb(34, 178, 34) if _mais_auth_rate > (
                                  self.voice_authentication.log_likelihood_threshold + 100 + self.face_recognition.confidence) / 2 else sg.rgb(
                              178, 34, 34))]],

                [sg.ButtonMenu("Sort", sort_types, key="sort"),
                 sg.Text("By latest", key="sort_label") if len(data) > 0 else [],
                 sg.ButtonMenu("Filter", filter_types, pad=((20, 0), (0, 0)), key="filter"),
                 sg.Text("All", key="filter_label") if len(data) > 0 else [],
                 sg.Text("User: ", pad=((20, 0), (0, 0))),
                 sg.InputText(key="user", size=(20, 1), enable_events=True)] if len(data) > 0 else [],

                [sg.Table(values=data, key="records", headings=["User", "Date", "Status", "Type"],
                          justification='center', auto_size_columns=False, col_widths=[30, 20, 12, 12, ], expand_y=True,
                          expand_x=False)] if len(data) > 0 else
                [sg.Text("There are no records of authentication yet", pad=((175, 0), (120, 0)), font=10)]
            ]

        else:
            data = None
            self.layout = [[sg.Image(self.assets_path + "access_denied.png", pad=((0, 0), (90, 0)))],
                           [sg.Text('ACCESS DENIED', pad=((0, 0), (20, 0)), font=(None, 12))],
                           [sg.Text("This is not for you, you should probably go home.")],
                           [sg.Button("Home", key="home_btn", pad=(0, 10))]]
            justification = 'center'

        try:
            window = sg.Window("DASHBOARD", self.layout, element_justification=justification, size=(720, 380))

            while True:
                event, values = window.read()
                if event == sg.WIN_CLOSED or event == 'Exit':
                    break

                if event == sg.Button("Exit") or event == "exit" or event == sg.Button("Home") or event == "home_btn":
                    window.close()
                    GUI.__init__(self, self.face_detector, self.face_recognition, self.voice_authentication)

                if (event == "filter" or event == "sort" or event == "user") and data and len(data) > 0:
                    shown_data = data

                    _filter = values["filter"]
                    if _filter == "Succeeded":
                        shown_data = [record for record in data if record[2] == "SUCCEEDED"]
                    elif _filter == "Failed":
                        shown_data = [record for record in data if record[2] == "FAILED"]
                    elif _filter == "Face ID":
                        shown_data = [record for record in data if record[3] == "Face ID"]
                    elif _filter == "Voice ID":
                        shown_data = [record for record in data if record[3] == "Voice ID"]

                    _user = values["user"]
                    if _user != "":
                        shown_data = [record for record in shown_data if _user in record[0]]

                    _sort = values['sort']
                    if _sort == "By oldest":
                        shown_data = sorted(shown_data, key=lambda row: row[1])
                    elif _sort == "By email":
                        shown_data = sorted(shown_data, key=lambda row: row[0])
                    else:
                        shown_data = sorted(shown_data, key=lambda row: row[1], reverse=True)
                    window['records'].update(values=shown_data)
                    window['sort_label'].update(value=_sort)
                    window['filter_label'].update(value=_filter)

        except Exception as err:
            sg.popup(err)
