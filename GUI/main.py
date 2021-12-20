#!/usr/bin/python3
import PySimpleGUI as sg
import cv2

class GUI:

    # Initialization function, main window
    def __init__(self, face_detector):

        self.capture_data = None
        self.face_detector = face_detector
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
                    window.close()
                    GUI.win_registration_picture(self)
                if event == sg.Cancel() or event == 'Cancel':
                    window.close()
                    GUI.__init__(self)

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
                    GUI.__init__(self)
        except Exception as err:
            sg.popup()
            window.close()

    # Confiramtion of registration window
    # ------------------------
    def win_registration_picture(self):
        # Interface layout
        # ------------------------
        try:
            self.layout = [[sg.Image(key='picture_registration')],
                           [sg.Button('Close')]]
            window = sg.Window('IMAGE', self.layout, size=(720,380), element_justification='center')
            self.capture_data = cv2.VideoCapture(0)  # Video capture (frames)

            while True:
                event, values = window.read(timeout=20)
                print(event, values)
                if event == sg.WIN_CLOSED or event == 'Exit':
                    break
                if event == sg.Button('Close') or event == 'Close':
                    window.close()
                    GUI.win_registration(self)

                if self.capture_data:
                    ret, img = self.capture_data.read()
                    if img is not None:
                        img, roi_gray, _ = self.face_detector.detect(img)
                        height = 240
                        width = int(img.shape[1] / (img.shape[0])/height)
                        img = cv2.resize(img, (width, height), interpolation=cv2.INTER_LINEAR)
                        img_bytes = cv2.imencode(".png", img)[1].tobytes()
                        window['picture_registration'].update(data=img_bytes)

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
                           [sg.Image(key='picture_authentication'), sg.Text('Email', size=(15,1)), sg.InputText(), sg.Submit()]]
            window = sg.Window("AUTHENTICATION", self.layout, size=(720, 380), element_justification='center')
            while True:
                event, values = window.read()
                print(event, values)  # Usunąć na końcu tę linijkę
                if event == sg.WIN_CLOSED or event == 'Exit':
                    break
                if event == sg.Submit() or event == 'Submit':
                    break #add here content
        except Exception as err:
            sg.popup()
            window.close()

    # Successfull confirmation of authentication process window
    # ------------------------
    def win_authentication_success(self):
        # Interface layout
        # ------------------------
        try:
            self.layout = [[sg.Text('SUCCESS! +YOU+ ARE AUTHENTICATED')]]
            window = sg.Window("SUCCESSFULL AUTHENTICATION", self.layout, size=(720, 380), element_justification='center')
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
        except Exception as err:
            sg.popup()
            window.close()

if __name__ == "__main__":
    GUI()
