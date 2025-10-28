from os import getenv
from sys import stdout

from uvicorn import run
from dotenv import load_dotenv

from app.main import app

PATH_TO_SERVER_ENV = '.env/server.env'
DEFAULT_HOST = '127.0.0.1'
DEFAULT_PORT = 30000
EXCEPTION_MESSAGE_HOST = f"{'-' * 40}\nCouldn't parse hostname from {PATH_TO_SERVER_ENV}, default host is {DEFAULT_HOST}\n{'-' * 40}\n"
EXCEPTION_MESSAGE_PORT = f"{'-' * 40}\nCouldn't parse port from {PATH_TO_SERVER_ENV}, default port is {DEFAULT_PORT}\n{'-' * 40}\n"


if __name__ == '__main__':
    load_dotenv(PATH_TO_SERVER_ENV)
    host = getenv('SERVER_HOST')
    port = getenv('SERVER_PORT')

    if not host:
        host = DEFAULT_HOST
        stdout.write(EXCEPTION_MESSAGE_HOST)
    else:
        host = str(host)

    #   Pylance не позволяет переводить в число тип str | None
    if not port:
        port = DEFAULT_PORT
        stdout.write(EXCEPTION_MESSAGE_PORT)
    else:
        port = int(port)

    run(app=app, host=host, port=port)
