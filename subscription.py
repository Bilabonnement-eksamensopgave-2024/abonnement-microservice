from dotenv import load_dotenv
import os
from datetime import datetime
import csv
import json
import firebase_admin
from firebase_admin import credentials, firestore

load_dotenv()
service_account_info = json.loads(os.getenv('GOOGLE_APPLICATION_CREDENTIALS_JSON')) 
cred = credentials.Certificate(service_account_info)
firebase_admin.initialize_app(cred)
db = firestore.client()

DB_NAME = os.getenv("DB_NAME")
TABLE_NAME = "subscriptions"

def create_table(): 
    with sqlite3.connect(DB_NAME) as conn: 
        cur = conn.cursor() 
        cur.execute(
            f'''CREATE TABLE {TABLE_NAME} 
            ( 
                subscription_id INTEGER PRIMARY KEY AUTOINCREMENT, 
                car_id INTEGER, 
                subscription_start_date TEXT, 
                subscription_end_date TEXT, 
                subscription_duration_months INTEGER DEFAULT 3, 
                km_driven_during_subscription INTEGER, 
                contracted_km INTEGER, 
                monthly_subscription_price INTEGER, 
                delivery_location TEXT, 
                has_delivery_insurance BOOLEAN DEFAULT FALSE 
            )'''
        ) 

def _add_csv_to_firestore():
    try:
        # Open the CSV file
        with open('subscriptions.csv', 'r', encoding='utf-8-sig') as file:
            reader = csv.DictReader(file)
            
            for row in reader:
                # Parse the dates from DD/MM/YYYY to YYYY-MM-DD
                start_date = datetime.strptime(row['SubscriptionStartDate'], '%d/%m/%Y').strftime('%Y-%m-%d')
                end_date = datetime.strptime(row['SubscriptionEndDate'], '%d/%m/%Y').strftime('%Y-%m-%d')
                
                # Add document to Firestore
                db.collection('subscriptions').document(str(row["SubscriptionId"])).set({
                    'car_id': int(row['CarId']),
                    'subscription_start_date': start_date,
                    'subscription_end_date': end_date,
                    'subscription_duration_months': int(row['SubscriptionDurationMonths']),
                    'km_driven_during_subscription': int(row['KmDrivenDuringSubscription']),
                    'contracted_km': int(row['ContractedKm']),
                    'monthly_subscription_price': float(row['MonthlySubscriptionPrice']),
                    'delivery_location': row['DeliveryLocation'],
                    'has_delivery_insurance': row['HasDeliveryInsurance'] == 'TRUE'
                })

        return [201, {"message": "CSV data imported successfully"}]

    except Exception as e:
        return [500, {"error": str(e)}]

def add_subscription(data):
    try:
        doc_ref = db.collection('subscriptions').document()
        
        doc_ref.set({
            'car_id': data.get('car_id'),
            'subscription_start_date': data.get('subscription_start_date'),
            'subscription_end_date': data.get('subscription_end_date'),
            'subscription_duration_months': data.get('subscription_duration_months', 3),
            'km_driven_during_subscription': data.get('km_driven_during_subscription'),
            'contracted_km': data.get('contracted_km'),
            'monthly_subscription_price': data.get('monthly_subscription_price'),
            'delivery_location': data.get('delivery_location'),
            'has_delivery_insurance': data.get('has_delivery_insurance', False)
        })

        return [201, {"message": "New subscription added to database"}]

    except Exception as e:
        return [500, {"error": str(e)}]

    
def get_subscriptions():
    try:
        subs_ref = db.collection('subscriptions')
        docs = subs_ref.stream()
        
        data = [doc.to_dict() for doc in docs]
        
        if not data:
            return [404, {"message": "Subscriptions not found"}]
                    
        return [200, data]

    except Exception as e:
        return [500, {"error": str(e)}]

    
def get_subscription_by_id(id):
    try:
        doc_ref = db.collection('subscriptions').document(str(id))
        doc = doc_ref.get()
        
        if not doc.exists:
            return [404, {"message": "Subscription not found"}]
                    
        return [200, doc.to_dict()]

    except Exception as e:
        return [500, {"error": str(e)}]


def get_active_subscriptions():
    try:
        today = datetime.now().strftime('%Y-%m-%d')
        subs_ref = db.collection('subscriptions')
        query = subs_ref.where('subscription_start_date', '<=', today).where('subscription_end_date', '>=', today)
        docs = query.stream()
        
        data = [doc.to_dict() for doc in docs]
        
        if not data:
            return [404, {"message": "Currently, there are no active subscriptions"}]
                    
        return [200, data]

    except Exception as e:
        return [500, {"error": str(e)}]


def get_active_subscriptions_total_price():
    try:
        today = datetime.now().strftime('%Y-%m-%d')
        subs_ref = db.collection('subscriptions')
        query = subs_ref.where('subscription_start_date', '<=', today).where('subscription_end_date', '>=', today)
        docs = query.stream()

        total_price = sum(doc.to_dict().get('monthly_subscription_price', 0) for doc in docs)
        
        return [200, {"total_price": total_price}]

    except Exception as e:
        return [500, {"error": str(e)}]


def update_subscription(id, data):
    try:
        doc_ref = db.collection('subscriptions').document(str(id))
        
        if not doc_ref.get().exists:
            return [404, {"message": "Subscription not found."}]

        doc_ref.update(data)
            
        return [201, {"message": "Subscription updated successfully."}]

    except Exception as e:
        return [500, {"error": str(e)}]


def delete_subscription_by_id(id):
    try:
        doc_ref = db.collection('subscriptions').document(str(id))
        
        if not doc_ref.get().exists:
            return [404, {"message": "Subscription not found."}]

        doc_ref.delete()
            
        return [200, {"message": "Subscription deleted successfully."}]

    except Exception as e:
        return [500, {"error": str(e)}]

