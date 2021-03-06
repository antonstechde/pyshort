import flask
from flask_restful import Api, Resource
from flask import redirect, request
from sql.interface import Interface
import configparser
from utils import utils
from flask_cors import CORS, cross_origin
import waitress
import sys

app = flask.Flask(__name__)
CORS(app)
api = Api(app)

config = configparser.ConfigParser()
config.read(utils.get_path(__file__) + "/config/config.ini")

sql_config = config["SQL"]
api_config = config["API"]

utils.set_sql_config(sql_config)
utils.set_main_file(__file__)
utils.set_Interface(Interface)

global debug


class UrlShortener(Resource):
    def get(self, short):
        """
        Redirects you to the page linked with the short
        :param short: A short to identify the full link
        :return:
        """
        url = utils.get_corresponding_url(short)
        if url is None:
            return "Not a valid redirect", 416  # Content does not exist
        return redirect(url)


class Home(Resource):
    def get(self):
        if request.host == "api.pyshort.de":
            return "You found our api endpoint :D here's our code: https://github.com/antonstechde/pyshort"
        return "Idk how you discovered the backend of the api endpoint, but here's our code: https://github.com/antonstechde/pyshort"

    def post(self):
        """
        Post request to add to the database
        :return: Status Code
        """
        host = request.host
        short = request.values.get("short")
        points_to = request.values.get("points_to")
        ip = request.values.get("ip")

        if short is None:
            short = utils.get_random_short()

        success_code = utils.add_to_database(host, short, points_to, ip)
        if success_code == 0:
            return f"Success! https://pyshort.de/{short}", 200

        elif success_code == 409:
            return f"Short {short} is already taken!", 409
        else:
            return "Internal database error", 500


api.add_resource(Home, '/')
api.add_resource(UrlShortener, '/<string:short>')
if "--debug" in sys.argv:
    debug = True
    app.run(host=api_config["api_host"], port=api_config["api_port"], debug=True)  # use in development

else:
    waitress.serve(app, host=api_config["api_host"], port=api_config["api_port"])  # run in production
