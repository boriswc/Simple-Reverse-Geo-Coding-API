# Simple Reverse Geo-Coding API

## Requirements

* Python Version >= 3.6
* Please see requirements.txt file that includes all necessary pip installations

## How to run? + install
* Install python3-pip : Execute "sudo apt-get install python3-pip" in terminal and press Y when prompted
* Execute "python3 -m pip install -r requirements.txt" in terminal
* Define the API_KEY environment variable with your Google API key  (export API_KEY=YOUR_GOOGLE_API_KEY for linux)
* Execute "python3 main.py"
* Send request through cURL or WGET (E.G: curl -i -X POST -F "file=@YOUR_CSV_FILE_PATH" http://127.0.0.1:5000/calculateDistances)

# Project Organization

    ├── requirements.txt         <- Requirements file (pip installations).
    ├── main.py                <- Main file. This file executes the project.

## Authors

* **Boris Wainstein** - *Programming* - [boriswc](https://github.com/boriswc)
