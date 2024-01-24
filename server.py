from flask import Flask, request, jsonify
import os
from xml.etree import ElementTree as ET
from tempfile import mkstemp
from shutil import move
from os import fdopen, remove

app = Flask(__name__)
#CORS(app)


def add_fill_attribute(svg_path, iso_3166_2, fill_color):
    # Parse the SVG file
    tree = ET.parse(svg_path)
    root = tree.getroot()

    # Find the path element with the specified iso_3166_2 code
    for path in root.findall('.//path[@iso_3166_2="' + iso_3166_2 + '"]'):
        # Add or update the fill attribute
        path.set('fill', fill_color)

    # Save the modified SVG to a new file
    modified_svg_path = svg_path.replace('.svg', '_modified.svg')
    tree.write(modified_svg_path)

    return modified_svg_path


def add_fill_attribute(xml_tree):
    # Define the namespace
    namespace = {'svg': 'http://www.w3.org/2000/svg'}

    # Iterate through elements with the correct namespace
    for path_element in xml_tree.findall('.//{http://www.w3.org/2000/svg}path[@iso_3166_2="RO-HD"]', namespace):
        # Add the "fill" attribute to the element
        path_element.set('fill', '#FF0000')



def parse_xml():
    import xml.etree.ElementTree as ET

    # Load the XML file
    tree = ET.parse('maps\\RO.svg')
    root = tree.getroot()
    

# Define the namespace
    namespace = {'svg': 'http://www.w3.org/2000/svg'}

    # Access elements and attributes with the namespace
    for path_element in root.findall('.//svg:path', namespace):
        print("Element:", path_element.tag)
        print("Attribute:", path_element.attrib)
        print("Text content:", path_element.text)
        print("-" * 30)


@app.route('/change-color', methods=['POST'])
def change_color_endpoint():
    print("aici")
    data = request.get_json()
    file_path = "C:\\Users\\Florin\\Desktop\\romania svg\\maps\\RO.svg"
    iso_code = data.get('iso_code')
    color = data.get('color')

    if not file_path or not iso_code or not color:
        return jsonify({'error': 'Missing parameters'}), 400

    if not os.path.exists(file_path):
        return jsonify({'error': 'File not found'}), 404

    try:
        print(file_path + "\n" + iso_code + " " + color)
        change_color_by_iso(file_path, iso_code, color)
        return jsonify({'message': 'Color changed successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


def remove_namespace_prefix(element):
    # Remove namespace prefix from element tag
    if '}' in element.tag:
        element.tag = element.tag.split('}', 1)[1]

if __name__ == '__main__':
    #app.run(debug=True)
    #parse_xml()
    # Load the XML file
    tree = ET.parse('maps\\RO.svg')

    # Call the function to add the attribute
    
    root = tree.getroot()
   
    add_fill_attribute(tree)
    root.set('xmlns', 'http://www.w3.org/2000/svg')
    for elem in root.iter():
        print(elem.attrib)
        remove_namespace_prefix(elem)
    add_fill_attribute(tree)
    tree.write('maps\\RO.svg', method='xml', xml_declaration=True)
