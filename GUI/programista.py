#!/usr/bin/python3
import PySimpleGUI as sg
import cv2

class GUI:

    # Initialization function, main window
    def __init__(self):

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
        capture_data = None
        try:
            # Interface layout
            # ------------------------
            self.layout = [[sg.Text('REGISTRATION', justification='center')],
                            [sg.Text('Name', size=(15, 1)), sg.InputText()],
                            [sg.Text('Email', size=(15, 1)), sg.InputText()],
                            [sg.Text('Password', size=(15, 1)), sg.InputText(password_char="*")],
                            [sg.Submit(), sg.Cancel()]]
            window = sg.Window("REGISTRATION", self.layout, size=(720, 380), element_justification='center')
            while True:
                event, values = window.read()
                print(event, values)  # Usunąć na końcu tę linijkę
                if event == sg.WIN_CLOSED or event == 'Exit':
                    break
                if event == sg.Submit() or event == 'Submit':
                    capture_data = cv2.VideoCapture(0) # Video capture (frames)
                    window.close()
                    GUI.win_registration_conf(self)
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
                           [sg.Button('Ok')]]
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
