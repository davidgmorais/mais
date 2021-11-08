import PySimpleGUI as sg
import cv2
import os.path
from objectDetectionPictureOpenCV import ObjectDetection


def main():
    # ----- Left column layout -----
    file_list_column = [
        [
            sg.Text("Image Folder"),
            sg.In(size=(25, 1), enable_events=True, key="-FOLDER-"),
            sg.FolderBrowse(),
        ],
        [
            sg.Listbox(
                values=[], enable_events=True, size=(40, 20), key="-FILE LIST-"
            )
        ],
    ]

    # ----- Right column layout -----
    image_viewer_column = [
        [sg.Text("Choose an image from list on left:")],
        [sg.Text(size=(40, 1), key="-TOUT-")],
        [sg.Image(key="-IMAGE-")],
        [sg.Button("Trigger object detection", key='-detection-', visible=False)]
    ]

    # --------- Full layout ---------
    layout = [
        [
            sg.Column(file_list_column),
            sg.VSeperator(),
            sg.Column(image_viewer_column),
        ]
    ]

    window = sg.Window("Image Viewer", layout)
    object_detector = ObjectDetection()
    selected, is_detection_on = None, False

    # Run the Event Loop
    while True:
        event, values = window.read()
        if event == "Exit" or event == sg.WIN_CLOSED:
            break

        # Folder name was filled in, make a list of files in the folder
        if event == "-FOLDER-":
            folder = values["-FOLDER-"]
            try:
                # Get list of files in folder
                file_list = os.listdir(folder)
            except:
                file_list = []

            f_names = [
                f
                for f in file_list
                if os.path.isfile(os.path.join(folder, f))
                and f.lower().endswith((".png", ".gif"))
            ]
            window["-FILE LIST-"].update(f_names)

        # A file was chosen from the listbox
        elif event == "-FILE LIST-":
            try:
                filename = os.path.join(
                    values["-FOLDER-"], values["-FILE LIST-"][0]
                )
                selected, is_detection_on = filename, False
                window["-TOUT-"].update(filename)
                window["-IMAGE-"].update(filename=filename)
                window["-detection-"].update(visible=True)
            except:
                pass

        # Detection button was clicked
        elif event == "-detection-" and selected:
            if is_detection_on:
                is_detection_on = False
                window["-IMAGE-"].update(filename=selected)
            else:
                is_detection_on = True
                output = object_detector.detect(selected)
                imgbytes = cv2.imencode('.png', output)[1].tobytes()  # ditto
                window["-IMAGE-"].update(data=imgbytes)

    window.close()


if __name__ == "__main__":
    main()
