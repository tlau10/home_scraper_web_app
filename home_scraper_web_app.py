from flask import Flask, render_template
from home_scraper_helper import read_json_file

app = Flask(__name__)

@app.route("/")
def hello():
    links = read_json_file(file_path = "list.json")
    return render_template('index.html', links = links["whitelist"], title = "Wohnungen")
