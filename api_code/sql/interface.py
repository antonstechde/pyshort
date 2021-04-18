from mysql.connector import connect
import mysql
import traceback


class Interface:
    def __init__(self, host_name, host_port, user_name, user_password, database_name):
        self.host_name = host_name
        self.host_port = host_port
        self.user_name = user_name
        self.user_password = user_password
        self.database_name = database_name
        self.connection = None
        self.cursor = None
        self.__create_connection__()

    def __create_connection__(self):
        """
        Establishes the connection between the database and the api
        :return:
        """
        try:
            self.connection = connect(
                host=self.host_name,
                port=self.host_port,
                user=self.user_name,
                passwd=self.user_password,
                database=self.database_name
            )
        except mysql.connector.errors.Error as e:
            print(f"An error has occured while connecting to the database!")
            traceback.print_exc()

        return self.connection

    def execute(self, query):
        """
        Executes a query
        :param query: The query to execute
        :return: The result of the query. Returns an empty list if there is no return value (for example in an 'insert into' query)
        """
        self.cursor = self.connection.cursor()
        self.cursor.execute(query)
        result = self.cursor.fetchall()
        self.cursor.close()
        return result

    def return_cursor(self, query):
        self.cursor = self.connection.cursor()
        self.cursor.execute(query)
        return self.cursor

    def close(self):
        """
        Commits the actions taken and closes the connection
        :return:
        """
        self.connection.commit()
        self.connection.close()
