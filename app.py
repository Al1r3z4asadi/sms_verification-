from flask import Flask , jsonify , request ,Response, redirect, url_for, session, abort
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user 
import requests
from pandas import read_excel
import sqlite3 , config


app = Flask(__name__)

# config
app.config.update(
    SECRET_KEY = config.FLASK_SECRET_KEY
)

# flask-login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


class User(UserMixin):

    def __init__(self, id):
        self.id = id
        
    def __repr__(self):
        return "%d" % (self.id)

user = User(0)

@app.route('/')
@login_required
def home():
    return Response("Hello World!")
 
# somewhere to login
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == 'POST': # TODO Stoping bruteforce  
        username = request.form['username']
        password = request.form['password']        
        if password == config.PASSWORD and username == config.USERNAME:

            login_user(user)
            return redirect(request.args.get(""))
        else:
            return abort(401)
    else:
        return Response('''
        <form action="" method="post">
            <p><input type=text name=username>
            <p><input type=password name=password>
            <p><input type=submit value=Login>
        </form>
        ''')


# somewhere to logout
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return Response('<p>Logged out</p>')


# handle login failed
@app.errorhandler(401)
def page_not_found(e):
    return Response('<p>Login failed</p>')
    
    
# callback to reload the user object        
@login_manager.user_loader
def load_user(userid):
    return User(userid)















def send_sms(receptor , message):
    
    my_api_key = '713831722B743341486E354A444D5466367A742F414758356457794B675172794955794364453836724A733D'
    url = f'https://api.kavenegar.com/v1/{my_api_key}/sms/send.json'
    data = {
        "receptor" : receptor,
        "message" : "we got your massage {}".format(receptor)
                }   
    res = requests.post(url , data=data)



def normalize_string(string):

    from_char = '۱۲۳۴۵۶۷۸۹۰'
    to_char = '1234567890'
    for i in range(len(from_char)):
        string = string.replace(from_char[i] , to_char[i])
    string = string.upper()
    return string







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
        start_serial = normalize_string(start_serial)
        end_serial = normalize_string(end_serial)
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

def check_serial(serial):
    """ will check if serial number is good or not"""
    conn = sqlite3.connect('serials.db')
    cur = conn.cursor()

    query = f"Select * From invalid_serials where invalid = '{serial}'"
    result = cur.execute(query)
    if len(result.fetchall()) == 1:
        return "This serial is among failed ones"


    query = f"Select * From valid_serials where start_serial < '{serial}' and end_serial > '{serial}'" 
    result = cur.execute(query)
    if len(result.fetchall()) == 1 :
        return "found your serial"

    return "it is not in the db"


@app.route('/v1/process',methods=['POST'])
def process():
    # import pdb;pdb.set_trace()
    form = request.form
    sender = form['from']
    message = normalize_string(form['message'])

    answer = check_serial(message)
    send_sms(sender , answer)
    return form


if __name__ == "__main__":
    import_database_from_excel('data.xlsx')
    print(check_serial("JJ104"))
    app.run('0.0.0.0' , 5000 , debug = True)
