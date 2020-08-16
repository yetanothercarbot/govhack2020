"""
Example Data: From IoT devices
time (seconds from 1970), sensor UID, item UID, UPC, store longitude, store latitude, purchase time(Seconds from 1970)

Example Data: From Mobile App
TimeOfSubmission,ImageData,type_of_plastic,GeoTagFromPhone
"""

from flask import Flask, request, url_for, flash, redirect
import sqlite3
import time
import datetime
import json
import os

DBF = "Data.db"

m_app_data = ['date', 'time', 'type_of_plastic', 'Longitude', 'Latitude']

LOGF = open("log.txt", 'w')
app = Flask(__name__)

@app.route('/sensor', methods=('GET', 'POST'))
def received_sensor():
    if request.method == "POST":
        data = request.get_data()
        return add_sensor_data_to_database(data.decode().split(','))
    else:
        return str(time.time())

@app.route('/m_app', methods=('GET', 'POST'))
def received_mobile_app():
    if request.method == 'POST':
        image = request.files['image']
        data = get_m_app_data(request)
        #os.chdir("images")
        #image.save(os.getcwd())
        location = os.path.join(os.getcwd(), image.filename)
        image.save(location)
        return add_app_data_into_database(location, data)
    else:
        return time.time()

@app.route('/sensorlist', methods=('GET',))
def received_sensorlist():
    return get_sensors(request)

@app.route('/api_overall', methods=('GET',))
def received_api_overall():
    return get_overall_stats(request)


def add_sensor_data_to_database(data:list):
    if len(data) != 7:
        return "510 Not Extended"
    try:
        DBConn = sqlite3.connect(DBF)
        readingDate, readingTime = tuple(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(data[0]))).split(' '))
        purchaseDate, purchaseTime = tuple(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(data[6]))).split(' '))
        c = DBConn.cursor()
        c.execute("INSERT INTO Data_From_Readers VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", (
            readingDate, readingTime, data[1], data[2], data[3], data[4], data[5], purchaseDate, purchaseTime))
        DBConn.commit()
        DBConn.close()
        return "201 Created"
    except Exception as e:
        LOGF.write("[{}]\t".format(str(datetime.datetime.now())) + str(e.with_traceback()) + "\n\n")
        LOGF.flush()
        print(e)
        return "500 Internal Server Error"

def add_app_data_into_database(location, data:list):
    if (len(data) != 5):
        return "510 Not Extended"
    try:
        DBConn = sqlite3.connect(DBF)
        c = DBConn.cursor()
        c.execute("INSERT INTO Data_From_App VALUES (?, ?, ?, ?, ?, ?)", (location, data[0], data[1], data[2], data[3], data[4]))
        DBConn.commit()
        DBConn.close()
        return "201 Created"
    except KeyboardInterrupt as e:
        LOGF.write("[{}]\t".format(str(datetime.datetime.now())) + str(e.with_traceback()) + "\n\n")
        LOGF.flush()
        print(e)
        return "500 Internal Server Error"

def get_m_app_data(request):
    data = []
    for field in m_app_data:
        data.append(str(request.form[field]))
    return data

def get_sensors(request):
    DBConn = sqlite3.connect(DBF)
    c = DBConn.cursor()
    c.execute("SELECT UDID, Location, Make, Model FROM Sensor_Information")
    sensors = c.fetchall()

    data = c.fetchall()

    DBConn.close()

    return json.dumps(data)

def get_overall_stats(request):
    DBConn = sqlite3.connect(DBF)
    c = DBConn.cursor()
    c.execute("SELECT count(*) FROM Data_From_Readers")
    count_all = c.fetchone()


    data = {
        'total': count_all[0],
    }

    DBConn.close()

    return json.dumps(data)

if __name__ == "__main__":
    app.run(port=8080)

