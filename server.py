import os
from flask import Flask, send_file, render_template

app = Flask(__name__)

@app.route('/')
def home():
    latest_files = os.listdir("./output_data")
    return render_template('downloads.html', downloads=latest_files)

@app.route("/download_file/<filename>")
def file_download(filename):
    return send_file("./output_data/"+filename)
    
port = os.getenv('PORT', '5000')    
if __name__ == "__main__":
    app.run()#host='0.0.0.0', port=int(port))