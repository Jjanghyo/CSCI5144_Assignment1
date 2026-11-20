import requests, os, logging, threading
from flask import Flask, request, Response
from uhashring import HashRing

# Get lists of KV Stores from environment variable
servers = os.getenv("KV_SERVERS").split(",")

app = Flask(__name__)

app.logger.setLevel(logging.INFO)

# Create HashRing
ring = HashRing(nodes = servers)

# Use thread-local storage to maintain a separate session for each thread
local = threading.local()

def get_session():
    if not hasattr(local, "session"):
        # Reuse HTTP connections
        local.session = requests.Session()
    return local.session

@app.route("/<string:key>", methods=["PUT", "POST", "GET", "DELETE"])
def route_node(key):
    # Find KV Store for the given key
    server = ring.get_node(key)
    app.logger.info("ROUTER: Key(%s) => %s", key, server)

    try:
        url = server + "/" + key

        # Send client's request to the selected KV Store
        response = get_session().request(
            method=request.method,
            url = url,
            json = request.get_json(silent=True),
            timeout = 5
        )

        # Return KV Store's response to the client
        return Response(
            response.content,
            status = response.status_code,
            content_type=response.headers.get("Content-Type"),
        )

    except requests.RequestException as e:
        app.logger.error("KV Store unavailable")
        return {"error": "KV Store unavailable"}, 502

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=os.getenv("PORT"), threaded=True)
