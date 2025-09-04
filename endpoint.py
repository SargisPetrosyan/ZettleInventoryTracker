from flask import Flask

app = Flask(__name__)

@app.route("/inventory_upload")
def inventory_updates():
    return "empty text"