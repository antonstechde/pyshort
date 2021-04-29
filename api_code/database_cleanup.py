import logging
import datetime
import time
import configparser
from sql.interface import Interface

from utils import utils
import sys
import os

config = configparser.ConfigParser()
config.read(utils.get_path(__file__) + "/config/config.ini")

sql_config = config["SQL"]

number_of_entries_removed = 0


def setup_logging():
    logFormat = logging.Formatter("%(asctime)s [%(threadName)s] [%(levelname)s]  %(message)s")
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    fileHandler = logging.FileHandler(utils.get_path(
        __file__) + f"/logs/database_checker/{datetime.datetime.now().strftime('%Y.%m.%d_%H-%M-%S')}.txt")
    fileHandler.setFormatter(logFormat)
    logger.addHandler(fileHandler)

    if "--quiet" not in sys.argv:
        consoleHandler = logging.StreamHandler(sys.stdout)
        consoleHandler.setFormatter(logFormat)
        logger.addHandler(consoleHandler)


def getInterface() -> Interface:
    global sql_config
    """
    Returns an connection interface with the corresponding values in config.ini
    :return: An connection interface
    """
    return Interface(sql_config["sql_host"], sql_config.getint("sql_port"), sql_config["sql_username"],
                     sql_config["sql_user_password"], sql_config["sql_database"])


def prettyfy_s(seconds):
    seconds = round(seconds, 2)

    minutes = 0
    while seconds > 60:
        minutes += 1
        seconds -= 60

    hours = 0
    while minutes > 60:
        hours += 1
        minutes -= 60

    return str(f"{hours} hours {minutes} minutes {seconds} seconds")


def analyze_file(file_path):
    global number_of_entries_removed
    interface = getInterface()
    data_file = file_path.rsplit("/")[-1]
    start = time.perf_counter()
    logging.info(f"Starting reading file {file_path.rsplit('/')[-1]}")
    with open(file_path, 'r') as f:
        content = f.readlines()
    logging.info(f"Took {time.perf_counter() - start}s to read {file_path.rsplit('/')[-1]}")

    results = interface.execute("select * from shorts")
    logging.info(f"Fetched database")
    logging.info(f"Starting comparison with codebase")
    start = time.perf_counter()
    logging.info(f"File {data_file} has {len(content)} entries to scan")
    for line in content:
        if line.startswith("#"):
            continue

        if line.startswith("0.0.0.0 "):
            line = line.split("0.0.0.0 ", 1)[-1]
        elif line.startswith("127.0.0.1 "):
            line = line.split("127.0.0.1 ", 1)[-1]

        if "#" in line:
            line = line.rsplit("#", 1)[0]

        line = line.strip()

        for res in results:
            entry_id, short, points_to, added_by_host, ip, clicks = res
            if line == points_to.replace("https://", "").replace("http://", ""):
                logging.info(
                    f"REMOVING: id: {entry_id}, short: {short}, points_to: {points_to}, added_by_host: {added_by_host}, clicks: {clicks}, because it matched {line} from {data_file}")
                interface.execute(f"delete from shorts where id='{entry_id}'")
                number_of_entries_removed += 1

    logging.info(
        f"Finished comparing file {file_path.rsplit('/')[-1]} to codebase in {prettyfy_s(time.perf_counter() - start)}")
    interface.close()


def remove_entry(entry_id):
    global number_of_entries_removed
    interface = getInterface()
    interface.execute(f"delete from shorts where id=%(entry_id)s", {"entry_id": entry_id})
    number_of_entries_removed += 1
    interface.close()


def clear_empty():
    """
    Deletes all empty and non-valid entries
    :return:
    """
    global number_of_entries_removed
    start = time.perf_counter()
    logging.info("Started clearing empty entries")
    interface = getInterface()
    database = interface.execute("select * from shorts")
    for res in database:
        entry_id, short, points_to, added_by_host, ip, clicks = res
        if points_to == 'None' or points_to is None or len(points_to) == 0 or points_to[:7] not in ["http://", "https:/"]:
            logging.info(
                f"REMOVING: id: {entry_id}, short: {short}, added_by_host: {added_by_host}, clicks: {clicks}, because entry was emtpy or invalid!")
            remove_entry(entry_id)

    interface.close()
    logging.info(f"Finished clearing empty entries in {prettyfy_s(time.perf_counter() - start)}")


if __name__ == '__main__':
    start = time.perf_counter()
    setup_logging()
    logging.info("Setup logging")

    clear_empty()

    all_dirs = os.listdir(utils.get_path(__file__) + "/checkList/")
    for i in all_dirs:
        all_files = os.listdir(utils.get_path(__file__) + f"/checkList/{i}/")
        for file in all_files:
            analyze_file(utils.get_path(__file__) + f"/checkList/{i}/{file}")

    logging.info("\n\nResults: "
                 f"\nTotal time spent running: {prettyfy_s(time.perf_counter() - start)}"
                 f"\nTotal amounts of entrys removed: {number_of_entries_removed}")
