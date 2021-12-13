#!/usr/bin/python3
import PySimpleGUI as sg
import cv2

class GUI:
    def __init__(self):
        sg.theme('Topanga')

        self.registration = "Registration"          #Variables that stores the name of buttons on the first display
        self.authentication = "Authentication"      #Variables that stores the name of buttons on the first display

        self.main_display_layout = [[sg.Text('WHAT DO YOU WANT TO DO ?')],
                       [sg.Button(self.registration), sg.Button(self.authentication)]]
        self.registration_layout = [[sg.Text('REGISTRATION', justification='center')],
                                    [sg.Text('Name', size=(15, 1)), sg.InputText()],
                                    [sg.Text('Email', size=(15, 1)), sg.InputText()],
                                    [sg.Text('Password', size=(15, 1)), sg.InputText(password_char="*")],
                                    [sg.Submit(), sg.Cancel()]
                                    ]
        self.picture_layout = [[sg.Image(key='picture'), sg.Cancel(), sg.Submit()]]
        self.confirmation_layout = [[sg.Text('EVERYTHING WENT WELL, \n YOU ARE REGISTERED.'), sg.Button('HOME', key='confirmation_button')]]
        self.authentication_layout = [[sg.Image(key='picture_authentication'), sg.Text('Email', size=(15,1)), sg.InputText(), sg.Submit()]]

        self.layout = [[sg.Column(self.main_display_layout, key='main_display')],
                       [sg.Column(self.registration_layout, visible=False, key='registration_display', vertical_alignment='center')],
                       [sg.Column(self.picture_layout, visible=False, key='picture_layout')],
                       [sg.Column(self.confirmation_layout, visible=False, key='confirmation_layout')],
                       [sg.Column(self.authentication_layout, visible=False, key='authentication_layout')]]


        window = sg.Window("MAIS", self.layout, size=(720,380), element_justification='center')
        cap = None

        while True:
            event, values = window.read()
            print(event, values)
            if event == sg.WIN_CLOSED or event == 'Exit':
                break
            if event == self.registration:
                window['main_display'].update(visible=False)
                window['registration_display'].update(visible=True)
            if event == 'Cancel':
                window['main_display'].update(visible=True)
                window['registration_display'].update(visible=False)
            if event == 'Submit':
                self.registration = values
                window['registration_display'].update(visible=False)
                window['picture_layout'].update(visible=True)
                cap = cv2.VideoCapture(0)
            if event == 'confirmation_button':
                window['confirmation_layout'].update(visible=False)
                window['main_display'].update(visible=True)
            if event == 'Cancel0':
                window['registration_display'].update(visible=True)
                window['picture_layout'].update(visible=False)
                if cap:
                    cap.release()
            if event == 'Submit1':
                window['picture_layout'].update(visible=False)
                window['confirmation_layout'].update(visible=True)
                if cap:
                    cap.release()
            if event == self.authentication:
                window['main_display'].update(visible=False)
                window['authentication_layout'].update(visible=True)
            if event == 'Submit2':
                window['main_display'].update(visible=True)
                window['authentication_layout'].update(visible=False)
            if cap:
                ret, img = cap.read()
                if img is not None:
                    print(ret)
                    imgbytes = cv2.imencode('.png', img)[1].tobytes()
                    window['picture'].update(data=imgbytes)

        window.close()

if __name__ == "__main__":
    GUI()
