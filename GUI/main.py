#!/usr/bin/python3
import PySimpleGUI as sg
import cv2

MAX_TRIES = 5

class GUI:

    # Initialization function, main window
    def __init__(self, face_detector, face_recognition):

        self.capture_data = None
        self.face_detector = face_detector
        self.face_recognition = face_recognition
        self.register_values = None
        self.authentication_values = None
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
                print(event, values) # Usunąć na końcu tę linijkę
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
            sg.popup()
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
                            [sg.Text('Password', size=(15, 1)), sg.InputText(password_char="*", key='password_registration')],
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
                    GUI.__init__(self, self.face_detector, self.face_recognition)

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
                           [sg.Button('Ok')],]
            window = sg.Window("CONFIRMATION", self.layout, size=(720, 380), element_justification='center')
            while True:
                event, values = window.read()
                print(event, values)  # Usunąć na końcu tę linijkę
                if event == sg.WIN_CLOSED or event == 'Exit':
                    break
                if event == sg.Button('Ok') or event == 'Ok':
                    window.close()
                    GUI.__init__(self, self.face_detector, self.face_recognition)
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
            window = sg.Window('IMAGE', self.layout, size=(720,380), element_justification='center')
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
                        width = int(img.shape[1] / (img.shape[0]/height))
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
                                    window.close()
                                    GUI.win_registration_conf(self)

            if self.capture_data:
                self.capture_data.release()
                self.capture_data = None

        except Exception as err:
            sg.popup()
            window.close()

    # Authentication window
    # ------------------------
    def win_authentication(self):
        # Interface layout
        # ------------------------
        try:
            self.layout = [[sg.Text('CONFIRMATION', justification='center')],
                           [sg.Text('Email', size=(15,1)), sg.InputText(key='email_authentication'), sg.Submit()]]
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

        except Exception as err:
            sg.popup()
            window.close()
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
                        if self.face_recognition.authenticate(self.authentication_values['email_authentication'], roi):
                            if self.capture_data:
                                self.capture_data.release()
                                self.capture_data = None
                            print("User authenticated, welcome!")
                            window.close()
                            GUI.win_authentication_success(self)

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



    # Successfull confirmation of authentication process window
    # ------------------------
    def win_authentication_success(self):
        # Interface layout
        # ------------------------
        try:
            self.layout = [[sg.Text('SUCCESS! +YOU+ ARE AUTHENTICATED')]]
            window = sg.Window("SUCCESSFULL AUTHENTICATION", self.layout, size=(720, 380), element_justification='center')

            while True:
                event, values = window.read()
                if event == sg.WIN_CLOSED or event == 'Exit':
                    window.close()

        except Exception as err:
            sg.popup()
            window.close()

    # Failed to authenticate user
    # ------------------------
    def win_authentication_fail(self):
        # Interface layout
        # ------------------------
        try:
            self.layout = [[sg.Text('FAILED TO AUTHENTICATE USER')]]
            window = sg.Window("FAILED TO AUTHENTICATE USER", self.layout, size=(720, 380), element_justification='center')

            while True:
                event, values = window.read()
                if event == sg.WIN_CLOSED or event == 'Exit':
                    break

        except Exception as err:
            sg.popup()
            window.close()


if __name__ == "__main__":
    GUI()
