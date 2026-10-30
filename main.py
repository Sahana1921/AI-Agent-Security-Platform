from flask import Flask
from flask_cors import CORS

from routes.prompt import prompt_bp
from dashboard import dashboard_bp
from database import create_database


app = Flask(__name__)

CORS(app)


create_database()


app.register_blueprint(
    prompt_bp,
    url_prefix="/api/prompt"
)

app.register_blueprint(
    dashboard_bp,
    url_prefix="/api/dashboard"
)


@app.route("/")
def home():

    return {
        "status": "success",
        "message": "AI Agent Security Platform Backend Running"
    }


@app.route("/health")
def health():

    return {
        "status": "healthy",
        "service": "AI Agent Security Platform"
    }


if __name__ == "__main__":

    print("==========================================")
    print("Starting AI Agent Security Platform Backend")
    print("==========================================")

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )