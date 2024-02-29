from flask import Flask, request, jsonify,render_template
import os
from xml.etree import ElementTree as ET
from tempfile import mkstemp
from shutil import move
from os import fdopen, remove
import http
app = Flask(__name__)
#CORS(app)

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
    tree = ET.parse('static\\maps\\RO.svg')  # Adjust the path as needed
    data = request.get_json()
    iso = data['iso']
    add_fill_attribute(tree, iso)
    tree.write('static\\maps\\updated_RO.svg')  # Save the updated SVG
    with open('static\\maps\\updated_RO.svg', 'r') as file:  # Read the updated SVG content
        svg_content = file.read()
    return jsonify({'svgContent': svg_content})  # Return the SVG content as JSON

if __name__ == '__main__':
    app.run(debug=True)   

