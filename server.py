from flask import Flask, request, jsonify,render_template,session,redirect,url_for,flash
import os
from xml.etree import ElementTree as ET
from tempfile import mkstemp
from shutil import move
from os import fdopen, remove
import re
import http
import image
from werkzeug.utils import secure_filename
import os
from time import sleep
from packaging import version
from flask import Flask, request, jsonify
import openai
from openai import OpenAI
import llm_utils
import pymysql
from flask_mysqldb import MySQL
import MySQLdb.cursors
from flask_wtf import FlaskForm
import hashlib
from wtforms import StringField, PasswordField, SubmitField, EmailField
from wtforms.validators import InputRequired, Length, ValidationError,EqualTo
import base64
from flask_cors import CORS
required_version = version.parse("1.1.1")
current_version = version.parse(openai.__version__)
OPENAI_API_KEY = os.environ['OPENAI_API_KEY']
if current_version < required_version:
  raise ValueError(f"Error: OpenAI version {openai.__version__}"
                   " is less than the required version 1.1.1")
else:
  print("OpenAI version is compatible.")



app = Flask(__name__)
CORS(app)
app.secret_key = 'your_secret_key'

client = OpenAI(
    api_key=OPENAI_API_KEY)  
assistant_id = llm_utils.create_assistant(client)


UPLOAD_FOLDER = 'uploads'


app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'cdss'
mysql = MySQL(app)
region_dict = {
    "RO-AB": "Alba",
    "RO-AR": "Arad",
    "RO-AG": "Argeș",
    "RO-BC": "Bacău",
    "RO-BH": "Bihor",
    "RO-BN": "Bistrița-Năsăud",
    "RO-BT": "Botoșani",
    "RO-BV": "Brașov",
    "RO-BR": "Brăila",
    "RO-BZ": "Buzău",
    "RO-CS": "Caraș-Severin",
    "RO-CL": "Călărași",
    "RO-CJ": "Cluj",
    "RO-CT": "Constanța",
    "RO-CV": "Covasna",
    "RO-DB": "Dâmbovița",
    "RO-DJ": "Dolj",
    "RO-GL": "Galați",
    "RO-GR": "Giurgiu",
    "RO-GJ": "Gorj",
    "RO-HR": "Harghita",
    "RO-HD": "Hunedoara",
    "RO-IL": "Ialomița",
    "RO-IS": "Iași",
    "RO-IF": "Ilfov",
    "RO-MM": "Maramureș",
    "RO-MH": "Mehedinți",
    "RO-MS": "Mureș",
    "RO-NT": "Neamț",
    "RO-OT": "Olt",
    "RO-PH": "Prahova",
    "RO-SM": "Satu Mare",
    "RO-SJ": "Sălaj",
    "RO-SB": "Sibiu",
    "RO-SV": "Suceava",
    "RO-TR": "Teleorman",
    "RO-TM": "Timiș",
    "RO-TL": "Tulcea",
    "RO-VS": "Vaslui",
    "RO-VL": "Vâlcea",
    "RO-VN": "Vrancea",
    "RO-B": "Bucharest (Municipality)"
}

def password_check(form, field):
    password = field.data
    if not re.search(r'[A-Z]', password):
        raise ValidationError('Password must contain at least one uppercase letter.')
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        raise ValidationError('Password must contain at least one special character.')

class LoginForm(FlaskForm):
    email= EmailField('Email', validators=[InputRequired(), Length(min=4, max=50)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=8, max=80)])
    submit = SubmitField('Login')

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(), Length(min=4, max=15)])
    email = EmailField('Email', validators=[InputRequired(), Length(min=6, max=50)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=8, max=80), password_check])
    retype_password = PasswordField('Retype Password', validators=[InputRequired(), EqualTo('password', message='Passwords must match.')])
    submit = SubmitField('Register')

class Alert:
    def __init__(self, id, image, user_id, disaster, region, time):
        self.id = id
        self.image = base64.b64encode(image).decode('utf-8')
        self.user_id = user_id
        self.disaster = disaster
        self.region = region
        self.time = time

    def to_dict(self):
        return {
            'id': self.id,
            'image': self.image,
            'user_id': self.user_id,
            'disaster': self.disaster,
            'region': self.region,
            'time': self.time
        }    

  
@app.route('/alerts', methods=['GET'])
def get_alerts():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM alerts ORDER BY time DESC")
    alerts = cursor.fetchall()
    cursor.close()
    alert_list = []
    for alert in alerts:
       alert_obj = Alert(
            id=alert['id'],
            user_id=alert['user_id'],
            image=alert['image'],
            disaster=alert['disaster'],
            region=alert['region'],
            time=alert['time']

        )
       alert_list.append(alert_obj.to_dict())
    return jsonify(alert_list)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        hashed_password = hashlib.sha256(password.encode('utf-8')).hexdigest()
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM users WHERE email = %s AND password = %s", (email, hashed_password))
        user = cursor.fetchone()
        cursor.close()
        
       
        if user:
            session['user_id'] = user['id']
            session['email'] = user['email']
            session['username'] = user['username']
            session['isAdmin'] = user['isAdmin'] 
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password')

    return render_template('login.html', form=form)

@app.route('/get_user_data', methods=['GET'])
def get_user_data():
    if 'user_id' in session:
        return jsonify({
            'user_id': session['user_id'],
            'email': session['email'],
         
            'isAdmin': session['isAdmin']
        })
    else:
        return jsonify({'error': 'User not logged in'}), 401

@app.route('/alerts/<int:alert_id>', methods=['DELETE'])
def delete_alert(alert_id):
    try:

        region_dict = {
            "Alba": "RO-AB",
            "Arad": "RO-AR",
            "Argeș": "RO-AG",
            "Bacău": "RO-BC",
            "Bihor": "RO-BH",
            "Bistrița-Năsăud": "RO-BN",
            "Botoșani": "RO-BT",
            "Brașov": "RO-BV",
            "Brăila": "RO-BR",
            "Buzău": "RO-BZ",
            "Caraș-Severin": "RO-CS",
            "Călărași": "RO-CL",
            "Cluj": "RO-CJ",
            "Constanța": "RO-CT",
            "Covasna": "RO-CV",
            "Dâmbovița": "RO-DB",
            "Dolj": "RO-DJ",
            "Galați": "RO-GL",
            "Giurgiu": "RO-GR",
            "Gorj": "RO-GJ",
            "Harghita": "RO-HR",
            "Hunedoara": "RO-HD",
            "Ialomița": "RO-IL",
            "Iași": "RO-IS",
            "Ilfov": "RO-IF",
            "Maramureș": "RO-MM",
            "Mehedinți": "RO-MH",
            "Mureș": "RO-MS",
            "Neamț": "RO-NT",
            "Olt": "RO-OT",
            "Prahova": "RO-PH",
            "Satu Mare": "RO-SM",
            "Sălaj": "RO-SJ",
            "Sibiu": "RO-SB",
            "Suceava": "RO-SV",
            "Teleorman": "RO-TR",
            "Timiș": "RO-TM",
            "Tulcea": "RO-TL",
            "Vaslui": "RO-VS",
            "Vâlcea": "RO-VL",
            "Vrancea": "RO-VN",
            "Bucharest (Municipality)": "RO-B"
        }

        cursor = mysql.connection.cursor()
    
        cursor.execute("SELECT region FROM alerts WHERE id = %s", (alert_id,))
        region_name = cursor.fetchone()
        region_name = region_name[0]

 
        iso = region_dict.get(region_name)
        
        cursor.execute("DELETE FROM alerts WHERE id = %s", (alert_id,))
        mysql.connection.commit()
        cursor.close()
        
        tree = ET.parse('static\\maps\\RO.svg')        
        add_fill_attribute_green(tree, iso)
        tree.write('static\\maps\\updated_RO.svg')  
        tree = ET.parse('static\\maps\\RO.svg')  
        remove_disaster_attribute(tree, iso)

        return redirect(url_for('index')), 200
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': 'Failed to delete alert'}), 500


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        password = form.password.data

        hashed_password = hashlib.sha256(password.encode('utf-8')).hexdigest()
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM users WHERE username = %s OR email = %s", (username, email))
        user = cursor.fetchone()

        if user:
            flash('Username or email already exists')
        else:
            cursor.execute("INSERT INTO users (username, email, password) VALUES (%s, %s, %s)", (username, email, hashed_password))
            mysql.connection.commit()
            cursor.close()
            flash('Registration successful! Please log in.')
            return redirect(url_for('login'))

    return render_template('register.html', form=form)



os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/Heimlich')
def heimlich():
    return render_template('/Heimlich.html')

@app.route('/FirstAid')
def firstAid():
    return render_template('/FirstAid.html')

@app.route('/CPR')
def CPR():
   return render_template('/CPR.html')

@app.route('/safe_position')
def safe_position():
    return render_template('/safe_position.html')

@app.route('/upload', methods=['POST', 'GET'])
def upload_file():

    if(session.get('user_id') is None):
        print(session.get('user_id'))
        return redirect(url_for('login'))
    

    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
 
    if file.filename == '':
        print('No selected file')
        return render_template('/index.html')

    if file:
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        with open(file_path, 'rb') as file:
            binary_data = file.read()
       


    print("image uploaded successfully")

    print('Disaster in region: ' + request.form['hiddenRegionChange'])
    
    
    dis = image.predict(file_path)
    if dis == 'Wildfire':
        dis = "Incendiu"
    
    elif dis == 'Flood':
         dis = "Inundatie"

    elif dis == 'Earthquake':
         dis = "Cutremur"

    elif dis == "Cyclone":
         dis = "Ciclon"



    tree = ET.parse('static\\maps\\RO.svg')
    iso = request.form['hiddenRegionChange']
    add_fill_attribute(tree, iso)
    tree.write('static\\maps\\updated_RO.svg')  
    with open('static\\maps\\updated_RO.svg', 'r') as file:  
        svg_content = file.read()


    
    tree = ET.parse('static\\maps\\RO.svg')
    print('[DEBUG]: Disaster: {}, Region: {}'.format(dis, iso))
    add_disaster_attribute(tree, iso, dis)

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    print(session['user_id'])
    iso = region_dict[iso]

    cursor.execute("INSERT INTO alerts (image, user_id, disaster, region, time) VALUES (%s, %s, %s, %s, NOW())", (binary_data, session['user_id'], dis, iso))
    mysql.connection.commit()
    cursor.close()


    tree.write('static\\maps\\updated_RO.svg')  # 
    with open('static\\maps\\updated_RO.svg', 'r') as file: 
        svg_content = file.read()





    return redirect(url_for('index'))


def add_disaster_attribute(xml_tree,iso,dis):
    
    namespace = {'svg': 'http://www.w3.org/2000/svg'}
    for path_element in xml_tree.findall(f'.//{{http://www.w3.org/2000/svg}}path[@iso_3166_2="{iso}"]', namespace):
        path_element.set('disaster', dis)

    root = xml_tree.getroot()
    root.set('xmlns', 'http://www.w3.org/2000/svg')
   
    for elem in root.iter():
        
        remove_namespace_prefix(elem)

    xml_tree.write('static\\maps\\RO.svg', method='xml', xml_declaration=True)

def remove_disaster_attribute(xml_tree,iso):
    namespace = {'svg': 'http://www.w3.org/2000/svg'}
    for path_element in xml_tree.findall(f'.//{{http://www.w3.org/2000/svg}}path[@iso_3166_2="{iso}"]', namespace):
        path_element.set('disaster', "")

    root = xml_tree.getroot()
    root.set('xmlns', 'http://www.w3.org/2000/svg')
   
    for elem in root.iter():
      
        remove_namespace_prefix(elem)

    xml_tree.write('static\\maps\\RO.svg', method='xml', xml_declaration=True)

def add_fill_attribute(xml_tree,iso):
    
    namespace = {'svg': 'http://www.w3.org/2000/svg'}
    for path_element in xml_tree.findall(f'.//{{http://www.w3.org/2000/svg}}path[@iso_3166_2="{iso}"]', namespace):
    
        path_element.set('fill', '#EE4E4E')

    root = xml_tree.getroot()
    root.set('xmlns', 'http://www.w3.org/2000/svg')
   
    for elem in root.iter():
        
        remove_namespace_prefix(elem)

    xml_tree.write('static\\maps\\RO.svg', method='xml', xml_declaration=True)


def add_fill_attribute_green(xml_tree,iso):
        
    namespace = {'svg': 'http://www.w3.org/2000/svg'}
    for path_element in xml_tree.findall(f'.//{{http://www.w3.org/2000/svg}}path[@iso_3166_2="{iso}"]', namespace):
    
        path_element.set('fill', '#A1DD70')

    root = xml_tree.getroot()
    root.set('xmlns', 'http://www.w3.org/2000/svg')
   
    for elem in root.iter():
     
        remove_namespace_prefix(elem)

    xml_tree.write('static\\maps\\RO.svg', method='xml', xml_declaration=True)


def remove_namespace_prefix(element):

    if '}' in element.tag:
        element.tag = element.tag.split('}', 1)[1]



@app.route('/logout')
def logout():
    print(session)
    session.clear()
    return redirect(url_for('login'))

@app.route('/')
def index():
    
    print (session)
    return render_template('index.html')

@app.route('/change-color', methods=['POST'])
def change_color_endpoint():
    
    print("INFO: Reached change-color endpoint")
    tree = ET.parse('static\\maps\\RO.svg') 
    data = request.get_json()
    print(data.keys())
    iso = data['iso']
    add_fill_attribute(tree, iso)
    tree.write('static\\maps\\updated_RO.svg')  # 
    with open('static\\maps\\updated_RO.svg', 'r') as file:  
        svg_content = file.read()


    return jsonify({'svgContent': svg_content}) 




@app.route('/landing')
def landing():
    return render_template('landing.html')


 # chatbot



@app.route('/start', methods=['GET'])
def start_conversation():
  print("Starting a new conversation...")  
  thread = client.beta.threads.create()
  print(f"New thread created with ID: {thread.id}") 
  return jsonify({"thread_id": thread.id})


@app.route('/chat', methods=['POST'])
def chat():
  data = request.json
  thread_id = data.get('thread_id')
  user_input = data.get('message', '')

  if not thread_id:
    print("Error: Missing thread_id")
    return jsonify({"error": "Missing thread_id"}), 400

  print(f"Received message: {user_input} for thread ID: {thread_id}")  
  client.beta.threads.messages.create(thread_id=thread_id,
                                      role="user",
                                      content=user_input)

  run = client.beta.threads.runs.create(thread_id=thread_id,
                                        assistant_id=assistant_id)

  
  while True:
    run_status = client.beta.threads.runs.retrieve(thread_id=thread_id,
                                                   run_id=run.id)
    print(f"Run status: {run_status.status}")
    if run_status.status == 'completed':
      break
    sleep(1)

  messages = client.beta.threads.messages.list(thread_id=thread_id)
  response = messages.data[0].content[0].text.value

  print(f"Assistant response: {response}")  
  return jsonify({"response": response})



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

