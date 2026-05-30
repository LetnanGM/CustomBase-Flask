from flask import Flask, render_template


class polyplay:
    def __init__(self) -> None:
        self.app: Flask = None

    def setup_me(self, app: Flask) -> None:
        self.app = app
        self.register_main_routes()

    def register_main_routes(self):
        @self.app.route("/login")
        def login_page() -> None:
            return render_template("login.html")
