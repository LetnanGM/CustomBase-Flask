# MAIN SECTION -

from application.bootstrap import WebServer

if __name__ == "__main__":
    serve = WebServer()(config=None)
    serve.deploy()
