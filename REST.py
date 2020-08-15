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
import os

DBF = "Data.db"

m_app_data = ['date', 'time', 'type_of_plastic', 'Longitude', 'Latitude']

LOGF = open("log.txt", 'w')
app = Flask(__name__)
IMG_ROOT = "./images"

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
        image.save(IMG_ROOT)
        #location = os.path.join(IMG_ROOT, image.name)
        #add_app_data_into_database(location, data)
        return ",".join(data) + "," + str(dir(image))
        #add_app_data_into_database(image, data.decode().split(','))


def add_sensor_data_to_database(data:list):
    if len(data) != 7:
        return "510 Not Extended"
    try:
        DBConn = sqlite3.connect(DBF)
        readingDate, readingTime = tuple(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(data[0]))).split(' '))
        purchaseDate, purchaseTime = tuple(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(data[6]))).split(' '))
        c = DBConn.cursor()
        c.execute("INSERT INTO Data_From_Readers VALUES ('{}','{}','{}', '{}', '{}', '{}', '{}', '{}', '{}')".format(
            readingDate, readingTime, data[1], data[2], data[3], data[4], data[5], purchaseDate, purchaseTime))
        DBConn.commit()
        DBConn.close()
        return "201 Created"
    except Exception as e:
        LOGF.write("[{}]\t".format(str(datetime.datetime.now())) + str(e) + "\n\n")
        LOGF.flush()
        print(e)
        return "500 Internal Server Error"

def add_app_data_into_database(image, data:list):
    DBConn = sqlite3.connect(DBF)
    c = DBConn.cursor()
    location = save(image)
    c.execute("INSERT INTO Data_From_App ('{}', '{}', '{}', '{}', '{}', '{}')".format(location, data[0], data[1], data[2], data[3], data[4]))
    DBConn.commit()
    DBConn.close()
    return "201 Created"

def get_m_app_data(request):
    data = []
    for field in m_app_data:
        data.append(str(request.form[field]))
    return data

if __name__ == "__main__":
    app.run(port=8080)
