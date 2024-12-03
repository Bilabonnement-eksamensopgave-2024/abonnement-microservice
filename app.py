from flask import Flask, jsonify, request, make_response
import requests
import sqlite3
import bcrypt
import os
import jwt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from dotenv import load_dotenv
from flasgger import swag_from
import datetime
from swagger.config import init_swagger
import subscription
#from auth import role_required

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
BASE_ADMIN_URL = ""

# Initialize Swagger
init_swagger(app)

# ----------------------------------------------------- GET /
@app.route('/', methods=['GET'])
def service_info():
    return jsonify({
        "service": "Subscriptions Microservice",
        "description": "This microservice handles subscription-related operations such as adding, updating, deleting, and retrieving subscriptions.",
        "endpoints": [
            {
                "path": "/subscriptions",
                "method": "GET",
                "description": "Retrieve a list of subscriptions",
                "response": "JSON array of subscription objects"
            },
            {
                "path": "/subscriptions/<int:id>",
                "method": "GET",
                "description": "Retrieve a specific subscription by ID",
                "response": "JSON object of a specific subscription or 404 error"
            },
            {
                "path": "/subscriptions/current",
                "method": "GET",
                "description": "Retrieve a list of current active subscriptions",
                "response": "JSON array of active subscription objects"
            },
            {
                "path": "/subscriptions/current/total-price",
                "method": "GET",
                "description": "Retrieve the total price of current active subscriptions",
                "response": "JSON object with total price or 404 error"
            },
            {
                "path": "/subscriptions/<int:id>/car",
                "method": "GET",
                "description": "Retrieve car information for a specific subscription by ID",
                "response": "JSON object with car information or 404 error"
            },
            {
                "path": "/subscriptions",
                "method": "POST",
                "description": "Add a new subscription",
                "response": "JSON object with a success message or error"
            },
            {
                "path": "/subscriptions/<int:id>",
                "method": "PATCH",
                "description": "Update an existing subscription",
                "response": "JSON object with a success message or 404 error"
            },
            {
                "path": "/subscriptions/<int:id>",
                "method": "DELETE",
                "description": "Delete a subscription by ID",
                "response": "JSON object with a success message or 404 error"
            }
        ]
    })

# ----------------------------------------------------- GET /subscriptions
@app.route('/subscriptions', methods=['GET'])
@swag_from('swagger/get_subscriptions.yaml')
#@role_required('user') # TODO UPDATE LATER
def subscriptions_get():    
    
    status, result = subscription.get_subscriptions()

    return jsonify(result), status

# ----------------------------------------------------- GET /subscriptions/id
@app.route('/subscriptions/<int:id>', methods=['GET'])
@swag_from('swagger/get_subscription_by_id.yaml')
#@role_required('user') # TODO UPDATE LATER
def get_subscription(id):    
    
    status, result = subscription.get_subscription_by_id(id)

    return jsonify(result), status

# ----------------------------------------------------- GET /subscriptions/id/car TODO
@app.route('/subscriptions/<int:id>/car', methods=['GET'])
@swag_from('swagger/get_subscription_car_info.yaml')
#@role_required('user') # TODO UPDATE LATER
def get_subscription_car_info(id):

    status, result = subscription.get_subscription_by_id(id)

    '''if status == 200:
        car_id = result.get("car_id")
        
        if car_id:
            url = f'{BASE_ADMIN_URL}/cars/{car_id}'
            headers = { 'Content-Type': 'application/json' } # TODO add token
            response = requests.get(url, headers=headers)
        
            return response.json(), response.status_code
        
        return jsonify({"message": "No car id found"}), 404'''
    
    return jsonify(result), status

# ----------------------------------------------------- GET /subscriptions/current
@app.route('/subscriptions/current', methods=['GET'])
@swag_from('swagger/get_current_subscriptions.yaml')
#@role_required('user') # TODO UPDATE LATER
def get_current_subscriptions():    
    
    status, result = subscription.get_active_subscriptions()

    return jsonify(result), status

# ----------------------------------------------------- GET /subscriptions/current/total-price
@app.route('/subscriptions/current/total-price', methods=['GET'])
@swag_from('swagger/get_current_subscriptions_total_price.yaml')
#@role_required('user') # TODO UPDATE LATER
def get_current_subscriptions_total_price():    
    
    status, result = subscription.get_active_subscriptions_total_price()

    return jsonify(result), status

# ----------------------------------------------------- POST /subscriptions
@app.route('/subscriptions', methods=['POST'])
@swag_from('swagger/post_subscriptions.yaml')
#@role_required('user') # TODO UPDATE LATER
def post_subscription():
    data = request.json
    
    status, result = subscription.add_subscription(data)

    # TODO update is_available under cars microservice
    '''if status == 201:
        car_update_status, car_update_result = _update_car_is_available(data)
        return jsonify(car_update_result), car_update_status'''

    return jsonify(result), status

# ----------------------------------------------------- PATCH /subscriptions/id
@app.route('/subscriptions/<int:id>', methods=['PATCH'])
@swag_from('swagger/patch_subscription.yaml')
#@role_required('user') # TODO UPDATE LATER
def patch_subscription(id):    
    data = request.json
    
    status, result = subscription.update_subscription(id, data)

    # TODO if date is changed or duration then update is_available under cars microservice
    '''if status == 201:
        start = data.get('subscription_start_date')
        end = data.get('subscription_end_date')
        duration = data.get('subscription_duration_months', 3)

        if start and end or duration and end:
            car_update_status, car_update_result = _update_car_is_available(data)
            return jsonify(car_update_result), car_update_status'''

    return jsonify(result), status

# ----------------------------------------------------- DELETE /subscriptions/id
@app.route('/subscriptions/<int:id>', methods=['DELETE'])
@swag_from('swagger/delete_subscription.yaml')
#@role_required('user') # TODO UPDATE LATER
def delete_subscription(id):        
    status, result = subscription.delete_item_by_id(id)

    return jsonify(result), status

def _is_available(start_date, end_date):
    # Calculate is_available based on subscription dates 
    today = datetime.now().strftime('%Y-%m-%d') 
    start_date = datetime.strptime(start_date, '%Y-%m-%d') 
    end_date = datetime.strptime(end_date, '%Y-%m-%d') 
    return start_date <= datetime.strptime(today, '%Y-%m-%d') <= end_date

def _update_car_is_available(data):
    car_id = data.get("car_id")
    start_date = data.get("subscription_start_date")
    end_date = data.get("subscription_end_date")
    
    if car_id and start_date and end_date:
        url = f'{BASE_ADMIN_URL}/cars/{car_id}'
        payload = { "is_available": _is_available(start_date, end_date) } 
        headers = { 'Content-Type': 'application/json' } # TODO add token
        response = requests.patch(url, json=payload, headers=headers)
    
        return response.json(), response.status_code
    
    return {"message": "No car id, start date or end date found"}, 404

    
if __name__ == '__main__':
    app.run()