from flask import Flask , jsonify , request 
import requests

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



def check_serial():
    pass 


if __name__ == "__main__":
    app.run('0.0.0.0' , 5000 , debug = True)
