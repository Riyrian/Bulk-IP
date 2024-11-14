from flask import Flask, request, render_template, jsonify
import requests
import json
import os
from bs4 import BeautifulSoup

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB limit

def get_ip_info(ip_address):
    try:
        # Get IP geolocation data
        url_geolocation = f"http://ip-api.com/json/{ip_address}"
        response_geolocation = requests.get(url_geolocation)
        data_geolocation = response_geolocation.json()
        
        if data_geolocation['status'] == 'success':
            ip_info = {
                "ip_address": ip_address,
                "country_code": data_geolocation.get("countryCode"),
                "country_name": data_geolocation.get("country"),
                "org_name": data_geolocation.get("org", "N/A"),
                "city": data_geolocation.get("city"),
                "postal_code": data_geolocation.get("zip"),
                "isp": data_geolocation.get("isp"),
                "latitude": data_geolocation.get("lat"),
                "longitude": data_geolocation.get("lon"),
                "region": data_geolocation.get("regionName"),
                "city_name": data_geolocation.get("city"),
            }

            # Get WHOIS data
            url_whois = f"https://whoisfreaks.com/tools/ip-whois/lookup/{ip_address}"
            ip_info["whois_url"] = url_whois

            return ip_info
        else:
            return {"error": data_geolocation.get("message", "Unknown error")}
    except requests.RequestException as e:
        return {"error": f"Request failed: {e}"}
    except json.JSONDecodeError:
        return {"error": "Failed to parse response"}

@app.route('/', methods=['GET', 'POST'])
def index():
    ip_info = []
    ip_addresses = []
    if request.method == 'POST':
        if 'ip_address' in request.form:
            ip_addresses = [request.form['ip_address']]
            ip_info = [get_ip_info(ip_addresses)]
        elif 'file' in request.files:
            file = request.files['file']
            if (file and file.filename.endswith('.txt')) or (file and file.filename.endswith('.csv')):
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
                file.save(file_path)
                with open(file_path, 'r') as f:
                    ip_addresses = [line.strip() for line in f.readlines()]
                    
    return render_template('index.html', ip_info=ip_info,ip_addresses=ip_addresses)

@app.route('/get_ip_info', methods=['POST'])
def get_ip_info_route():
    ipAddress = request.form['ip_address']
    ip_info = get_ip_info(ipAddress)
    return jsonify(ip_info)

if __name__ == "__main__":
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(debug=True)
