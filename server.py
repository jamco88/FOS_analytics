import os
import requests
from flask import Flask, send_from_directory, render_template
from werkzeug.utils import secure_filename
from scraper.scraper import scrape_ahead_n_complaints
from config import FILE_NAME
from main import create_output_tables
app = Flask(__name__)


@app.route('/')
def home():
    latest_output_files = [file for file in os.listdir("./output_data") if file.endswith(".csv")]
    latest_scrape_files = [file for file in os.listdir(os.path.dirname(FILE_NAME))]
    return render_template('downloads.html', outputs=latest_output_files, scrapes=latest_scrape_files)


@app.route("/download_file/<library>/<filename>")
def file_download(filename, library):
    if library == "output":
        dl_dir = "./output_data/"
    elif library == "scrapes":
        dl_dir = os.path.dirname(FILE_NAME)
    return send_from_directory(dl_dir, secure_filename(filename), as_attachment=True)


port = os.getenv('PORT', '5000')
if __name__ == "__main__":
    scrape_ahead_n_complaints(n_ahead=30)
    create_output_tables()
    app.run(host='0.0.0.0', port=int(port), debug=True)
