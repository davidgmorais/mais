import mysql.connector
import hashlib

config = {
    'host': 'localhost',
    'port': 3306,
    'user': 'admin',
    'password': 'pass',
    'database': 'mais'
}
# docker run --name=mais-db -p 3306:3306 -e MYSQL_ROOT_PASSWORD=_secret -e MYSQL_USER=admin -e MYSQL_PASSWORD=pass
# -e MYSQL_DATABASE=mais -d mysql/mysql-server:latest


class DatabaseManager:

    def __connect(self):
        """
        Private function to connect to the database
        """
        try:
            self.__conn = mysql.connector.connect(**config)
            print("Connection established")
        except mysql.connector.Error as err:
            print(err)

    def __init__(self):
        self.__conn = None
        self.__connect()

    # user methods
    def get_users(self):
        if not self.__conn:
            return None

        query = "SELECT id FROM USER;"
        cursor = self.__conn.cursor()
        cursor.execute(query)
        users = [user[0] for user in cursor.fetchall()]
        cursor.close()
        self.__conn.commit()
        return users

    def get_user_id_by_email(self, email):
        if not self.__conn:
            return None

        query = "SELECT id FROM USER WHERE email = %s;"
        cursor = self.__conn.cursor()
        cursor.execute(query, [email])
        user_id = cursor.fetchone()
        cursor.close()

        return user_id[0]

    def user_exists_by_email(self, email):
        if not self.__conn:
            return None

        query = f"SELECT email FROM USER WHERE email = %s;"
        cursor = self.__conn.cursor()
        cursor.execute(query, [email])
        users = cursor.fetchall()
        cursor.close()

        if len(users) > 0:
            return True
        return False

    def add_user(self, email, password):
        if not self.__conn:
            return None

        user_query = "INSERT INTO USER (email, password) VALUES (%s, %s)"
        cursor = self.__conn.cursor()
        password = hashlib.sha256(password.encode(encoding='utf-8')).hexdigest()
        cursor.execute(user_query, [email, password])
        cursor.reset()

    def get_user_passphrase_by_email(self, email):
        if not self.__conn:
            return None

        query = "SELECT passphrase FROM USER WHERE email = %s;"
        cursor = self.__conn.cursor()
        cursor.execute(query, [email])
        passphrase = cursor.fetchone()
        cursor.close()

        if passphrase:
            passphrase[0].split(" ")
        return passphrase

    def update_user_passphrase_by_user_id(self, passphrase, user_id):
        if not self.__conn:
            return False

        passphrase_query = "UPDATE USER SET passphrase = %s WHERE id = %s;"
        cursor = self.__conn.cursor()
        cursor.execute(passphrase_query, [passphrase, user_id])
        cursor.close()
        self.__conn.commit()

    # image methods
    def get_images_by_user(self, user_id):
        if not self.__conn:
            return None

        query = "SELECT image, mac FROM IMAGE WHERE user_id = %s;"
        cursor = self.__conn.cursor()
        cursor.execute(query, [user_id])
        image_list = cursor.fetchall()
        cursor.close()
        return [(image[0], image[1]) for image in image_list]

    def add_images(self, images):
        if not self.__conn:
            return None

        query = "INSERT INTO IMAGE (image, mac, user_id) VALUES (%s, %s, %s)"
        cursor = self.__conn.cursor()
        cursor.executemany(query, images)
        cursor.close()
        self.__conn.commit()

    # wav methods
    def get_wavs_by_user(self, user_id):
        if not self.__conn:
            return None

        query = "SELECT voice, mac FROM WAV WHERE user_id = %s"
        cursor = self.__conn.cursor()
        cursor.execute(query, [user_id])
        wav_list = cursor.fetchall()
        cursor.close()
        return [(wav[0], wav[1]) for wav in wav_list]

    def add_waves(self, samples):
        if not self.__conn:
            return None

        query = "INSERT INTO WAV (voice, mac, user_id) VALUE (%s, %s, %s);"
        cursor = self.__conn.cursor()
        cursor.executemany(query, samples)
        cursor.close()
        self.__conn.commit()

    # utils methods
    def close(self):
        """
        Closes the database connection, if it is established.
        """

        if self.__conn:
            self.__conn.close()
            print("Connection closed")
