from flask import Flask
import views
from waitress import serve

def create_app():
    app = Flask(__name__)
    app.register_blueprint(views.image_bp)
    return app

if __name__ == '__main__':
    app = create_app()
    serve(app, host = "0.0.0.0" ,port=80)


# Run with python -m app.app