import sys
from GUI.main import GUI
from database.database_manager import DatabaseManager
from face_detection import FaceDetector
from face_recognition import FaceRecognition
from voice_authentication import VoiceAuthentication


def create_system_admin(database, _email):
    if not database.user_exists_by_email(_email):
        print("User not found, please create a user before executing this action")
        return

    if database.give_admin_privileges_by_email(_email):
        print("Admin privileges were given to", _email)
        return

    print("Something went wrong, action aborted.")


def remove_system_admin(database, _email):
    if not database.user_exists_by_email(_email):
        print("User not found, please create a user before executing this action")
        return

    if database.remove_admin_privileges_by_email(_email):
        print("Admin privileges were removed from", _email)
        return

    print("Something went wrong, action aborted.")


def main():
    database = DatabaseManager()
    if len(sys.argv) == 3:
        _email = sys.argv[2]
        if sys.argv[1] == "createadmin":
            create_system_admin(database, _email)
        elif sys.argv[1] == "removeadmin":
            remove_system_admin(database, _email)
        else:
            print("Invalid command")

    else:
        face_detector = FaceDetector(0.3, 2)
        face_recognition = FaceRecognition(database, confidence=65.0)
        voice_auth = VoiceAuthentication(database, confidence=90)
        GUI(face_detector, face_recognition, voice_auth)
    database.close()


if __name__ == "__main__":
    main()
