import os

os.environ["DYNAMODB_TABLE_NAME"] = "passengers"
os.environ["AWS_REGION"] = "us-east-1"
os.environ["AWS_ACCESS_KEY_ID"] = "fake_access_key"
os.environ["AWS_SECRET_ACCESS_KEY"] = "fake_secret_key"
os.environ["AWS_SECURITY_TOKEN"] = "fake_security_token"
os.environ["AWS_ENDPOINT_URL"] = "http://localhost:5001"

from flask import Flask
from moto import server
from prediction_handler import lambda_handler
from mock_api.mock_dynamodb import create_table
from mock_api.mock_event import (
    mock_post_passenger_event,
    mock_get_all_passengers_event,
    mock_get_passenger_by_id_event,
    mock_delete_passenger_event
)
from flask import jsonify


post_passenger_event = mock_post_passenger_event()
get_all_passengers_event = mock_get_all_passengers_event()


app = Flask(__name__)

@app.route("/sobreviventes", methods=["POST"])
def sobreviu():
    return lambda_handler(post_passenger_event, None)

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "OK"}), 200

@app.route("/sobreviventes", methods=["GET"])
def get_all_passengers():
    return lambda_handler(get_all_passengers_event, None)

@app.route("/sobreviventes/<string:passenger_id>", methods=["GET"])
def get_passenger(passenger_id):
    return lambda_handler(mock_get_passenger_by_id_event(passenger_id), None)

@app.route("/sobreviventes/<string:passenger_id>", methods=["DELETE"])
def delete_passenger(passenger_id):
    return lambda_handler(mock_delete_passenger_event(passenger_id), None)

if __name__ == "__main__":
    server = server.ThreadedMotoServer(port=5001)
    
    try:
        server.start()
        # create_table()
        print("DynamoDB table created successfully.")
        app.run(host="0.0.0.0", port=9091, debug=True)

    except Exception as e:
        print(f"Error starting Moto server: {e}")   

    finally:
        server.stop()
        print("Moto server stopped.")