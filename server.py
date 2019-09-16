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
import json
app = Flask(__name__)


@app.route('/')
def home():
    latest_output_files = [file for file in os.listdir("./output_data") if file.endswith(".csv")]
    run_dates = json.load(open('run_info.json'))
    scraped_nums = get_retrieved_complaints()
    return render_template('downloads.html',
                           outputs=latest_output_files,
                           num_files=len(scraped_nums),
                           application_logging=run_dates,
                           latest_file=max(scraped_nums)
                           )


@app.route("/download_file/<library>/<filename>")
def file_download(filename, library):
    if library == "output":
        dl_dir = "./output_data/"
    elif library == "scrapes":
        dl_dir = os.path.dirname(FILE_NAME)
    return send_from_directory(dl_dir, secure_filename(filename), as_attachment=True)


def scrape_run():
    print('Scraping: %s' % datetime.now())
    if len(get_retrieved_complaints()) == 1:
        scrape_ahead_n_complaints(n_ahead=74000)
    else:
        scrape_ahead_n_complaints(n_ahead=1500)

    data = json.load(open('run_info.json'))
    data["scrape"] = "Last scrape successfully executed at " + datetime.strftime(datetime.today(), "%d-%m-%Y %H:%M")
    with open("run_info.json", "w") as f:
        json.dump(data, f)


def analytics_run():
    print('Creating analytics tables: %s' % datetime.now())
    create_output_tables()
    data = json.load(open('run_info.json'))
    data["analytics"] = "Output tables last created at " + datetime.strftime(datetime.today(), "%d-%m-%Y %H:%M")
    with open("run_info.json", "w") as f:
        json.dump(data, f)


def schedule_analytics_run():
    """"""
    scheduler = BackgroundScheduler()
    # Add a scheduled run from restart so tables are populated
    scheduler.add_job(analytics_run, "date", run_date=datetime.now().replace(minute=datetime.now().minute+1))

    scheduler.add_job(scrape_run, "cron", day_of_week="mon,wed-fri", hour=0, minute=0)
    scheduler.add_job(analytics_run, "cron", day_of_week="sat,tue", hour=0, minute=0)
    scheduler.start()


port = os.getenv('PORT', '5000')
if __name__ == "__main__":
    schedule_analytics_run()
    app.run(host='0.0.0.0', port=int(port))
