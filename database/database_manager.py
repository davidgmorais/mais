import datetime

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
        try:
            query = "INSERT INTO USER (email, password) VALUES (%s, %s)"
            cursor = self.__conn.cursor()
            password = hashlib.sha256(password.encode(encoding='utf-8')).hexdigest()
            cursor.execute(query, [email, password])
            cursor.close()
            self.__conn.commit()
        except mysql.connector.Error as err:
            print(err)
            return False
        return True

    def remove_user(self, user_id):
        if not self.__conn:
            return None
        try:
            query = "DELETE FROM USER WHERE id = %s"
            cursor = self.__conn.cursor()
            cursor.execute(query, [user_id])
            cursor.close()
            self.__conn.commit()
        except mysql.connector.Error as err:
            print(err)
            return False
        return True

    def get_user_passphrase_by_email(self, email):
        if not self.__conn:
            return None

        query = "SELECT passphrase FROM USER WHERE email = %s;"
        cursor = self.__conn.cursor()
        cursor.execute(query, [email])
        passphrase = cursor.fetchone()
        cursor.close()

        if passphrase:
            passphrase = passphrase[0].split(" ")
        return passphrase

    def update_user_passphrase_by_user_id(self, passphrase, user_id):
        if not self.__conn:
            return False

        try:
            passphrase_query = "UPDATE USER SET passphrase = %s WHERE id = %s;"
            cursor = self.__conn.cursor()
            cursor.execute(passphrase_query, [passphrase, user_id])
            cursor.close()
            self.__conn.commit()
        except mysql.connector.Error as err:
            print(err)
            return False
        return True

    def give_admin_privileges_by_email(self, email):
        if not self.__conn:
            return None
        if not self.user_exists_by_email(email):
            return False

        try:
            query = "UPDATE USER SET admin_flag = 1 WHERE email = %s"
            cursor = self.__conn.cursor()
            cursor.execute(query, [email])
            cursor.close()
            self.__conn.commit()
        except mysql.connector.Error as err:
            print(err)
            return False
        return True

    def remove_admin_privileges_by_email(self, email):
        if not self.__conn:
            return None
        if not self.user_exists_by_email(email):
            return False

        try:
            query = "UPDATE USER SET admin_flag = 0 WHERE email = %s"
            cursor = self.__conn.cursor()
            cursor.execute(query, [email])
            cursor.close()
            self.__conn.commit()
        except mysql.connector.Error as err:
            print(err)
            return False
        return True

    def is_admin_by_email(self, email):
        if not self.__conn:
            return None

        query = "SELECT admin_flag FROM USER WHERE email = %s"
        cursor = self.__conn.cursor()
        cursor.execute(query, [email])
        user = cursor.fetchall()
        cursor.close()
        if len(user) != 1:
            return False
        is_admin = user[0][0]
        return is_admin

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

        try:
            query = "INSERT INTO IMAGE (image, mac, user_id) VALUES (%s, %s, %s)"
            cursor = self.__conn.cursor()
            cursor.executemany(query, images)
            cursor.close()
            self.__conn.commit()
        except mysql.connector.Error as err:
            print(err)
            return False
        return True

    def remove_images_by_user_id(self, user_id):
        if not self.__conn:
            return None
        try:
            query = "DELETE FROM IMAGE WHERE user_id = %s"
            cursor = self.__conn.cursor()
            cursor.execute(query, [user_id])
            cursor.close()
            self.__conn.commit()
        except mysql.connector.Error as err:
            print(err)
            return False
        return True

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
        try:
            query = "INSERT INTO WAV (voice, mac, user_id) VALUE (%s, %s, %s);"
            cursor = self.__conn.cursor()
            cursor.executemany(query, samples)
            cursor.close()
            self.__conn.commit()
        except mysql.connector.Error as err:
            print(err)
            return False
        return True

    # record methods
    def __check_for_duplicate_records(self, user_id, module, status, date):
        if not self.__conn:
            return None
        if module not in ['Face ID', 'Voice ID']:
            return None
        if status not in ["SUCCEEDED", "FAILED"]:
            return None

        try:
            query = "SELECT id, date FROM RECORD WHERE type = %s AND  user_id = %s AND status = %s"
            cursor = self.__conn.cursor()
            cursor.execute(query, [module, user_id, status])
            records = cursor.fetchall()
            cursor.close()
            for record_id, record_date in records:
                elapsed = date - datetime.datetime.strptime(record_date, '%Y-%m-%d %H:%M:%S')
                if abs(elapsed) < datetime.timedelta(seconds=2):
                    return record_id

        except mysql.connector.Error as err:
            print(err)
        return None

    def log_record(self, user_id, module, status):
        if not self.__conn:
            return None
        if module not in ['Face ID', 'Voice ID']:
            return False
        try:
            _date = datetime.datetime.now()
            _formatted_date = _date.strftime('%Y-%m-%d %H:%M:%S')
            _status = "SUCCEEDED" if status else "FAILED"

            record_id = self.__check_for_duplicate_records(user_id, module, _status, _date)
            if record_id:
                query = "UPDATE RECORD SET date = %s, status = %s WHERE id = %s"
                values = [_formatted_date, _status, record_id]

            else:
                query = "INSERT INTO RECORD (date, type, status, user_id) VALUES (%s, %s, %s, %s);"
                values = [_formatted_date, module, _status, user_id]

            cursor = self.__conn.cursor()
            cursor.execute(query, values)
            cursor.close()
            self.__conn.commit()
        except mysql.connector.Error as err:
            print(err)
            return False
        return True

    def get_records(self, module):
        if not self.__conn:
            return None
        if module not in ['Face ID', 'Voice ID']:
            return False

        query = "SELECT USER.email, RECORD.date, RECORD.status, RECORD.type FROM RECORD INNER JOIN USER on RECORD.user_id = USER.id WHERE type = %s"
        cursor = self.__conn.cursor()
        cursor.execute(query, [module])
        records = [[rec[0], datetime.datetime.strptime(rec[1], '%Y-%m-%d %H:%M:%S'), rec[2], rec[3]] for rec in cursor.fetchall()]
        cursor.close()
        return records

    # utils methods
    def close(self):
        """
        Closes the database connection, if it is established.
        """

        if self.__conn:
            self.__conn.close()
            print("Connection closed")
