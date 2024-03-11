from flask import Flask, request, jsonify,render_template
import os
from xml.etree import ElementTree as ET
from tempfile import mkstemp
from shutil import move
from os import fdopen, remove
import http
import image
from werkzeug.utils import secure_filename
app = Flask(__name__)
#CORS(app)

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

