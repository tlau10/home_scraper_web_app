from flask import Flask, render_template, redirect, url_for
from home_scraper_helper import read_json_file
from home_scraper import add_to_blacklist, remove_from_whitelist

app = Flask(__name__)

@app.route("/")
def hello():
    links = read_json_file(file_path = "list.json")
    return render_template('index.html', links = links["whitelist"], title = "Wohnungen")

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def delete(path):
    remove_from_whitelist(item = path)
    add_to_blacklist(item = path)
    return redirect("/")
