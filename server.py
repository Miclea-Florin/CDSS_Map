from flask import Flask, request, jsonify,render_template
import os
from xml.etree import ElementTree as ET
from tempfile import mkstemp
from shutil import move
from os import fdopen, remove
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

required_version = version.parse("1.1.1")
current_version = version.parse(openai.__version__)
OPENAI_API_KEY = os.environ['OPENAI_API_KEY']
if current_version < required_version:
  raise ValueError(f"Error: OpenAI version {openai.__version__}"
                   " is less than the required version 1.1.1")
else:
  print("OpenAI version is compatible.")



app = Flask(__name__)
#CORS(app)

client = OpenAI(
    api_key=OPENAI_API_KEY)  
assistant_id = llm_utils.create_assistant(client)


UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/FirstAid')
def firstAid():
    return render_template('/FirstAid.html')

@app.route('/safe_position')
def safe_position():
    return render_template('/safe_position.html')

@app.route('/upload', methods=['POST', 'GET'])
def upload_file():
    # Check if the post request has the file part
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    # If the user does not select a file, the browser submits an
    # empty file without a filename.
    if file.filename == '':
        print('No selected file')
        return render_template('/index.html')
        #return jsonify({'error': 'No selected file'}), 400
    if file:
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        # You can now process the file as needed
        #return jsonify({'message': 'File uploaded successfully', 'filename': filename}), 200
    print("image uploaded successfully")
   # print(request.form['hiddenRegionChange'])
    print('Disaster in region: ' + request.form['hiddenRegionChange'])
    
    
    dis = image.predict(file_path)
    
    #TO DELETE IF DOESN"T WORK
    tree = ET.parse('static\\maps\\RO.svg')
    iso = request.form['hiddenRegionChange']
    add_fill_attribute(tree, iso)
    tree.write('static\\maps\\updated_RO.svg')  # Save the updated SVG
    with open('static\\maps\\updated_RO.svg', 'r') as file:  # Read the updated SVG content
        svg_content = file.read()

    #print('[DEBUG]: '+str(type(dis)) + str(dis))
    
    tree = ET.parse('static\\maps\\RO.svg')
    print('[DEBUG]: Disaster: {}, Region: {}'.format(dis, iso))
    add_disaster_attribute(tree, iso, dis)
    tree.write('static\\maps\\updated_RO.svg')  # Save the updated SVG
    with open('static\\maps\\updated_RO.svg', 'r') as file:  # Read the updated SVG content
        svg_content = file.read()





    return render_template('/index.html')


def add_disaster_attribute(xml_tree,iso,dis):
    
    namespace = {'svg': 'http://www.w3.org/2000/svg'}
    for path_element in xml_tree.findall(f'.//{{http://www.w3.org/2000/svg}}path[@iso_3166_2="{iso}"]', namespace):
        path_element.set('disaster', dis)

    root = xml_tree.getroot()
    root.set('xmlns', 'http://www.w3.org/2000/svg')
   
    for elem in root.iter():
        #print(elem.attrib)
        remove_namespace_prefix(elem)

    xml_tree.write('static\\maps\\RO.svg', method='xml', xml_declaration=True)



def add_fill_attribute(xml_tree,iso):
    
    namespace = {'svg': 'http://www.w3.org/2000/svg'}
    for path_element in xml_tree.findall(f'.//{{http://www.w3.org/2000/svg}}path[@iso_3166_2="{iso}"]', namespace):
    
        path_element.set('fill', '#FF0000')

    root = xml_tree.getroot()
    root.set('xmlns', 'http://www.w3.org/2000/svg')
   
    for elem in root.iter():
        #print(elem.attrib)
        remove_namespace_prefix(elem)

    xml_tree.write('static\\maps\\RO.svg', method='xml', xml_declaration=True)


def remove_namespace_prefix(element):

    if '}' in element.tag:
        element.tag = element.tag.split('}', 1)[1]


@app.route('/')
def index():
    return render_template('/index.html')

@app.route('/change-color', methods=['POST'])
def change_color_endpoint():
    
    print("INFO: Reached change-color endpoint")
    tree = ET.parse('static\\maps\\RO.svg')  # Adjust the path as needed
    data = request.get_json()
    print(data.keys())
    iso = data['iso']
    add_fill_attribute(tree, iso)
    tree.write('static\\maps\\updated_RO.svg')  # Save the updated SVG
    with open('static\\maps\\updated_RO.svg', 'r') as file:  # Read the updated SVG content
        svg_content = file.read()


    return jsonify({'svgContent': svg_content})  # Return the SVG content as JSON





 # chatbot

@app.route('/start', methods=['GET'])
def start_conversation():
  print("Starting a new conversation...")  # Debugging line
  thread = client.beta.threads.create()
  print(f"New thread created with ID: {thread.id}")  # Debugging line
  return jsonify({"thread_id": thread.id})

# Generate response
@app.route('/chat', methods=['POST'])
def chat():
  data = request.json
  thread_id = data.get('thread_id')
  user_input = data.get('message', '')

  if not thread_id:
    print("Error: Missing thread_id")  # Debugging line
    return jsonify({"error": "Missing thread_id"}), 400

  print(f"Received message: {user_input} for thread ID: {thread_id}")  # Debugging line

  # Add the user's message to the thread
  client.beta.threads.messages.create(thread_id=thread_id,
                                      role="user",
                                      content=user_input)

  # Run the Assistant
  run = client.beta.threads.runs.create(thread_id=thread_id,
                                        assistant_id=assistant_id)

  # Check if the Run requires action (function call)
  while True:
    run_status = client.beta.threads.runs.retrieve(thread_id=thread_id,
                                                   run_id=run.id)
    print(f"Run status: {run_status.status}")
    if run_status.status == 'completed':
      break
    sleep(1)  # Wait for a second before checking again

  # Retrieve and return the latest message from the assistant
  messages = client.beta.threads.messages.list(thread_id=thread_id)
  response = messages.data[0].content[0].text.value

  print(f"Assistant response: {response}")  # Debugging line
  return jsonify({"response": response})



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

