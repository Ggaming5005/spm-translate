import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# Function to process OSM data and scale it
def process_osm_data(osm_xml, scale):
    import xml.etree.ElementTree as ET
    root = ET.fromstring(osm_xml)

    nodes = []
    ways = []

    # Extract nodes
    for node in root.findall('node'):
        node_id = node.attrib['id']
        lat = float(node.attrib['lat']) * scale
        lon = float(node.attrib['lon']) * scale
        nodes.append({"id": node_id, "lat": lat, "lon": lon})

    # Extract ways
    for way in root.findall('way'):
        way_id = way.attrib['id']
        node_refs = [nd.attrib['ref'] for nd in way.findall('nd')]
        ways.append({"id": way_id, "nodes": node_refs})

    return {"nodes": nodes, "ways": ways}

@app.route('/getMapData', methods=['GET'])
def get_map_data():
    bbox = request.args.get('bbox')  # Bounding box: minLon,minLat,maxLon,maxLat
    scale = float(request.args.get('scale', 0.1))  # Default scale factor is 0.1
    
    if not bbox:
        return jsonify({"error": "Bounding box is required (minLon,minLat,maxLon,maxLat)"}), 400
    
    # Fetch OSM data
    osm_url = f"https://api.openstreetmap.org/api/0.6/map?bbox={bbox}"
    response = requests.get(osm_url)

    if response.status_code == 200:
        osm_data = response.text
        processed_data = process_osm_data(osm_data, scale)
        return jsonify(processed_data)
    else:
        return jsonify({"error": "Failed to fetch OSM data", "status": response.status_code}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
