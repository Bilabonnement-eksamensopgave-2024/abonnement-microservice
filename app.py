from flask import Flask, jsonify, request, make_response
import requests
import os
from dotenv import load_dotenv
from flasgger import swag_from
from datetime import datetime
from swagger.config import init_swagger
import subscription
import auth

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
ADMIN_EMAIL = os.getenv('ADMIN_EMAIL')
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD')
ADMIN_GATEWAY_URL = os.getenv('ADMIN_GATEWAY_URL')

cookies = None

# Initialize Swagger
init_swagger(app)

# ----------------------------------------------------- Private functions
def _login():
    global cookies
    if cookies == None or 'Authorization' not in cookies:
        url = f'{ADMIN_GATEWAY_URL}/user/login' 

        response = requests.post( 
            url, 
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}, 
            headers={'Content-Type': 'application/json'},
            ) 
        
        if response.status_code == 200: 
            cookies = response.cookies
            return True
        return False 
    return True

def _is_available(start_date, end_date):
    try:
        # Calculate is_available based on subscription dates 
        today = datetime.now().strftime('%Y-%m-%d') 
        start_date = datetime.strptime(start_date, '%Y-%m-%d') 
        end_date = datetime.strptime(end_date, '%Y-%m-%d') 
        is_available = not (start_date <= datetime.strptime(today, '%Y-%m-%d') <= end_date)
        return [200, is_available]

    except Exception as e:
        return [500, {"error": str(e)}]

def _update_car_is_available(data):
    car_id = data.get("car_id")
    start_date = data.get("subscription_start_date")
    end_date = data.get("subscription_end_date")
    
    if car_id and start_date and end_date:
        is_available = _is_available(start_date, end_date)
        if is_available[0] == 200:
            if _login():
                url = f'{ADMIN_GATEWAY_URL}/car/cars/{car_id}'
                payload = { "is_available": is_available[1] } 
                headers = { 'Content-Type': 'application/json' }
                response = requests.patch(url, json=payload, headers=headers, cookies=cookies)
                return response.json(), response.status_code
            
            return {"message": "Authentication failed"}, 401
        
        return {"message": f"Could not calculate is_available: {is_available[1]}"}, 404
    
    return {"message": "No car id, start date or end date found"}, 404

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
                "role_required": "admin, finance, sales"
            },
            {
                "path": "/subscriptions/<int:id>",
                "method": "GET",
                "description": "Retrieve a specific subscription by ID",
                "role_required": "admin, sales"
            },
            {
                "path": "/subscriptions/current",
                "method": "GET",
                "description": "Retrieve a list of current active subscriptions",
                "role_required": "admin"
            },
            {
                "path": "/subscriptions/current/total-price",
                "method": "GET",
                "description": "Retrieve the total price of current active subscriptions",
                "role_required": "admin, finance"
            },
            {
                "path": "/subscriptions/<int:id>/car",
                "method": "GET",
                "description": "Retrieve car information for a specific subscription by ID",
                "role_required": "admin, sales"
            },
            {
                "path": "/subscriptions",
                "method": "POST",
                "description": "Add a new subscription",
                "role_required": "admin, sales"
            },
            {
                "path": "/subscriptions/<int:id>",
                "method": "PATCH",
                "description": "Update an existing subscription",
                "role_required": "admin, sales"
            },
            {
                "path": "/subscriptions/<int:id>",
                "method": "DELETE",
                "description": "Delete a subscription by ID",
                "role_required": "admin, sales"
            }
        ]
    })

# ----------------------------------------------------- GET /subscriptions                                                                                                                                  
@app.route('/subscriptions', methods=['GET'])
@swag_from('swagger/get_subscriptions.yaml')
@auth.role_required('admin', 'finance', 'sales') 
def subscriptions_get():
    
    status, result = subscription.get_subscriptions()

    return jsonify(result), status

# ----------------------------------------------------- GET /subscriptions/id
@app.route('/subscriptions/<int:id>', methods=['GET'])
@swag_from('swagger/get_subscription_by_id.yaml')
@auth.role_required('admin', 'sales')
def get_subscription(id):    
    
    status, result = subscription.get_subscription_by_id(id)

    return jsonify(result), status

# ----------------------------------------------------- GET /subscriptions/id/car
@app.route('/subscriptions/<int:id>/car', methods=['GET'])
@swag_from('swagger/get_subscription_car_info.yaml')
@auth.role_required('admin', 'sales') 
def get_subscription_car_info(id):
    status, result = subscription.get_subscription_by_id(id)

    if status == 200:
        car_id = result.get("car_id")
        
        if car_id:
            if _login():
                url = f'{ADMIN_GATEWAY_URL}/car/cars/{car_id}'
                headers = { 'Content-Type': 'application/json' }
                response = requests.get(url, headers=headers, cookies=cookies)
            
                return response.json(), response.status_code
            
            return jsonify({"message": "Authentication failed"}), 401
        
        return jsonify({"message": "No car id found"}), 404
    
    return jsonify(result), status

# ----------------------------------------------------- GET /subscriptions/current
@app.route('/subscriptions/current', methods=['GET'])
@swag_from('swagger/get_current_subscriptions.yaml')
@auth.role_required('admin')
def get_current_subscriptions():
    
    status, result = subscription.get_active_subscriptions()

    return jsonify(result), status

# ----------------------------------------------------- GET /subscriptions/current/total-price
@app.route('/subscriptions/current/total-price', methods=['GET'])
@swag_from('swagger/get_current_subscriptions_total_price.yaml')
@auth.role_required('admin', 'finance') 
def get_current_subscriptions_total_price():
    
    status, result = subscription.get_active_subscriptions_total_price()

    return jsonify(result), status

# ----------------------------------------------------- POST /subscriptions
@app.route('/subscriptions', methods=['POST'])
@swag_from('swagger/post_subscriptions.yaml')
@auth.role_required('admin', 'sales')
def post_subscription():
    data = request.json
    
    status, result = subscription.add_subscription(data)
    response_data = {"subscription": {"result": result, "status": status}}

    if status == 201:
        car_update_status, car_update_result = _update_car_is_available(data)
        response_data["car_update"] = {"result": car_update_result, "status": car_update_status}
        return jsonify(response_data), car_update_status

    return jsonify(response_data), status

# ----------------------------------------------------- PATCH /subscriptions/id
@app.route('/subscriptions/<int:id>', methods=['PATCH'])
@swag_from('swagger/patch_subscription.yaml')
@auth.role_required('admin', 'sales') 
def patch_subscription(id):    
    data = request.json
    
    status, result = subscription.update_subscription(id, data)
    response_data = {"subscription": {"result": result, "status": status}}

    if status == 201:
        start = data.get('subscription_start_date')
        end = data.get('subscription_end_date')
        duration = data.get('subscription_duration_months', 3)

        if start and end or duration and end:
            car_update_status, car_update_result = _update_car_is_available(data)
            response_data["car_update"] = {"result": car_update_result, "status": car_update_status}
            return jsonify(response_data), car_update_status

    return jsonify(result), status

# ----------------------------------------------------- DELETE /subscriptions/id
@app.route('/subscriptions/<int:id>', methods=['DELETE'])
@swag_from('swagger/delete_subscription.yaml')
@auth.role_required('admin', 'sales') 
def delete_subscription(id):        
    status, result = subscription.delete_item_by_id(id)

    return jsonify(result), status

# ----------------------------------------------------- GET /health
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"}), 200
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5006)))