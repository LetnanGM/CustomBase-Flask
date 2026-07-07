# MAIN SECTION -

from .bootstrap.bootstrap import WebServer

def main():
    serve = WebServer()(config=None)
    serve.deploy()

if __name__ == "__main__":
    main()