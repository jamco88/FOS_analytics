import os
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from flask import Flask, send_from_directory, render_template
from werkzeug.utils import secure_filename
from scraper.scraper import scrape_ahead_n_complaints
from config import FILE_NAME
from main import create_output_tables
from datetime import datetime, timedelta
from scraper.scraper import get_retrieved_complaints
app = Flask(__name__)


@app.route('/')
def home():
    latest_output_files = [file for file in os.listdir("./output_data") if file.endswith(".csv")]
    #latest_scrape_files = [file for file in os.listdir(os.path.dirname(FILE_NAME))]
    scraped_nums = get_retrieved_complaints()
    return render_template('downloads.html',
                           outputs=latest_output_files,
                           num_files=len(scraped_nums),
                           latest_file=max(scraped_nums)
                           )


@app.route("/download_file/<library>/<filename>")
def file_download(filename, library):
    if library == "output":
        dl_dir = "./output_data/"
    elif library == "scrapes":
        dl_dir = os.path.dirname(FILE_NAME)
    return send_from_directory(dl_dir, secure_filename(filename), as_attachment=True)


def analytics_run():
    print('Scraping and running: %s' % datetime.now())
    if len(get_retrieved_complaints()) == 1:
        scrape_ahead_n_complaints(n_ahead=74000)
    else:
        #scrape_ahead_n_complaints(n_ahead=5000)
        create_output_tables()


def schedule_analytics_run():
    """"""
    scheduler = BackgroundScheduler()
    midnight = (datetime.now() + timedelta(minutes=1))#.replace(hour=0, minute=0, second=0, microsecond=0)
    scheduler.add_job(analytics_run, trigger=IntervalTrigger(days=2, start_date=midnight))
    scheduler.start()


port = os.getenv('PORT', '5000')
if __name__ == "__main__":
    schedule_analytics_run()
    app.run(host='0.0.0.0', port=int(port))
