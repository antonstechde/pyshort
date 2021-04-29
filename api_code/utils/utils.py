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
    """

    :rtype: object
    """
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
    increment_click(short)
    res = res[0]
    res, = res
    return res


def add_to_database(host, short, points_to, ip) -> int:
    """
    Adds a database entry
    :param host: The host from where the request is coming from, either api.uwuwhatsthis.de or api.pyshort.de
    :param short: The short that should be created
    :param points_to: The url that should poin to the short
    :return:
    """
    try:
        interface = getInterface()
        exec_string = "INSERT INTO shorts (short, points_to, added_by_host, added_by_ip, clicks) value (%(short)s, %(points_to)s, %(host)s, %(ip)s, %(clicks)s);"
        # print(f"Executing: {exec_string}")
        if get_corresponding_url(short) is None:
            interface.execute(exec_string, {"short": short, "points_to": points_to, "host": host, "ip": ip, "clicks": 0})
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


def increment_click(short):
    interface = getInterface()
    res = interface.execute("select clicks from shorts where short=%(short)s", {"short": short})
    res = res[0]
    res, = res
    res = int(res) + 1
    interface.execute("update shorts set clicks =%(res)s where short =%(short)s", {"res": res, "short": short})
    interface.close()

