import pathlib
import random
import string

main_file = None
sql_config = None
Interface = None


def set_main_file(file):
    global main_file
    main_file = file


def set_sql_config(config):
    global sql_config
    sql_config = config


def set_Interface(interface):
    global Interface
    Interface = interface


def get_path(file) -> str:
    return str(pathlib.Path(file).parent.absolute())


def getInterface() -> Interface:
    global sql_config
    """
    Returns an connection interface with the corresponding values in config.ini
    :return: An connection interface
    """
    return Interface(sql_config["sql_host"], sql_config.getint("sql_port"), sql_config["sql_username"],
                     sql_config["sql_user_password"], sql_config["sql_database"])


def get_corresponding_url(short):
    """
    'Converts' the short url to a full url and redirects you
    :param short: the url-short
    :return: the full url that is linked with the short
    """
    interface = getInterface()

    res = interface.execute(f"select points_to from shorts where short=%(short)s", {"short": short})
    interface.close()

    if len(res) == 0:
        return None
    res = res[0]
    res, = res
    if not res.startswith("https://") or res.startswith("http://"):
        res = f"http://{res}"
    return res


def add_to_database(host, short, points_to) -> int:
    """
    Adds a database entry
    :param host: The host from where the request is coming from, either api.uwuwhatsthis.de or api.pyshort.de
    :param short: The short that should be created
    :param points_to: The url that should poin to the short
    :return:
    """
    try:
        interface = getInterface()
        exec_string = "INSERT INTO shorts (short, points_to, added_by_host) value (%(short)s, %(points_to)s, %(host)s);"
        # print(f"Executing: {exec_string}")
        if get_corresponding_url(short) is None:
            interface.execute(exec_string, {"short": short, "points_to": points_to, "host": host})
            interface.close()
            return 0  # Success: Everything's fine
        else:
            interface.close()
            return 409  # Conflict: Already exists
    except Exception as e:

        print(e)
        return 500  # Internal Server Error: Something failed within the database


def get_random_short(length: int = 5) -> str:
    while True:
        generated_short = ""
        for i in range(length):
            generated_short += random.choice(string.ascii_letters)

        if get_corresponding_url(generated_short) is None:
            return generated_short

