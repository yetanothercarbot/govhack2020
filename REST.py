"""
Example Data:
time (seconds from 1970), sensor UID, item UID, UPC, store longitude, store latitude, purchase time(Seconds from 1970)
"""

from flask import Flask, request, url_for, flash, redirect
import sqlite3
import time
import datetime

DBF = "Data.db"

LOGF = open("log.txt", 'w')
app = Flask(__name__)

@app.route('/', methods=('GET', 'POST'))
def received():
    if request.method == "POST":
        data = request.get_data()
        return add_data_to_database(data.decode().split(','))
    else:
        return str(time.time())


def add_data_to_database(data):
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

if __name__ == "__main__":
    app.run(port=8080)