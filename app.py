from flask import Flask , jsonify , request 
import requests
from pandas import read_excel
import sqlite3


app = Flask(__name__)

def send_sms(receptor , message):
    
    my_api_key = '713831722B743341486E354A444D5466367A742F414758356457794B675172794955794364453836724A733D'
    url = f'https://api.kavenegar.com/v1/{my_api_key}/sms/send.json'
    data = {
        "receptor" : receptor,
        "message" : "we got your massage {}".format(receptor)
                }   
    res = requests.post(url , data=data)


@app.route('/v1/process',methods=['POST'])
def process():
    # import pdb;pdb.set_trace()
    form = request.form
    sender = form['from']
    message = form['message']
    send_sms(sender , message)
    return form



def normalize_string(str):
    











def import_database_from_excel(filepath):


    '''frist sheet contains serial data and the second sheet contains invalid serial numbers which contains one column
        this data will be written in the sql database 
    '''



    conn = sqlite3.connect('serials.db')
    cur = conn.cursor()

    #remove the serials table if exists then create  a new one
    cur.execute('Drop table if exists valid_serials')
    cur.execute(""" create table if not exists valid_serials (
        id Integer primary key,
        ref text , 
        desc text , 
        start_serial integer , 
        end_serial text , 
        date DATE
    );""")

    df = read_excel(filepath , 0)
    serials_counter = 0

    for index , (line , ref , desc , start_serial , end_serial , date ) in df.iterrows():
        query = f'Insert into valid_serials values ("{line}" , "{ref}" , "{desc}" ,"{start_serial}" ,"{end_serial}" , "{date}" )'
        cur.execute(query)
        if serials_counter & 7 == 0 :# commits each 8 query
            conn.commit()
        serials_counter+=1
    conn.commit()



    cur.execute('Drop table if exists invalid_serials')
    cur.execute(""" create table if not exists invalid_serials (
        invalid Text primary key
    );""")

    df = read_excel(filepath , 1)
    invalid_counter = 0 
    for index , (failed_serial_row) in df.iterrows():
        failed_serial = failed_serial_row[0]    
        query = f'insert into invalid_serials values ( "{failed_serial}" )'
        cur.execute(query)
        if invalid_counter & 7 == 0 :
            conn.commit()
        invalid_counter+=1
    conn.commit()
    conn.close()

    #returning how many valid and invalid serials added to the database 
    return (serials_counter, invalid_counter)

def check_serial():
    pass 


if __name__ == "__main__":
    # app.run('0.0.0.0' , 5000 , debug = True)
     import_database_from_excel('data.xlsx')