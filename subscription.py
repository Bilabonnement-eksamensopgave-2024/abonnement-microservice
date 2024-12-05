import sqlite3
from datetime import datetime
import csv
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()
DB_PATH = os.getenv('DB_PATH')
TABLE_NAME = "subscriptions"

def create_table(): 
    with sqlite3.connect(DB_PATH) as conn: 
        cur = conn.cursor() 
        cur.execute(
            f'''CREATE TABLE IF NOT EXISTS {TABLE_NAME} 
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
create_table()

def _add_csv_to_db():
    try: 
        with sqlite3.connect(DB_PATH) as conn: 
            cur = conn.cursor() 
            # Open the CSV file 
            with open('subscriptions.csv', 'r') as file: 
                reader = csv.DictReader(file) 
                for row in reader: 
                    # Parse the dates from DD/MM/YYYY to YYYY-MM-DD 
                    start_date = datetime.strptime(row['SubscriptionStartDate'], '%d/%m/%Y').strftime('%Y-%m-%d') 
                    end_date = datetime.strptime(row['SubscriptionEndDate'], '%d/%m/%Y').strftime('%Y-%m-%d') 
                    
                    cur.execute( 
                        f''' INSERT OR IGNORE INTO {TABLE_NAME} 
                        ( 
                            car_id, 
                            subscription_start_date, 
                            subscription_end_date, 
                            subscription_duration_months, 
                            km_driven_during_subscription, 
                            contracted_km, 
                            monthly_subscription_price, 
                            delivery_location, 
                            has_delivery_insurance 
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?) ''', 
                        ( 
                            row['CarId'], 
                            start_date, 
                            end_date, 
                            row['SubscriptionDurationMonths'], 
                            row['KmDrivenDuringSubscription'], 
                            row['ContractedKm'], 
                            row['MonthlySubscriptionPrice'], 
                            row['DeliveryLocation'], 
                            row['HasDeliveryInsurance'] == 'TRUE'
                        ) 
                    )
                    
        return [201, {"message": "CSV data imported successfully"}] 
    
    except sqlite3.Error as e: return [500, {"error": str(e)}]
        
def add_subscription(data):
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cur = conn.cursor()
            
            cur.execute(
                f''' INSERT OR IGNORE INTO {TABLE_NAME} 
                ( 
                    car_id, 
                    subscription_start_date, 
                    subscription_end_date, 
                    subscription_duration_months, 
                    km_driven_during_subscription, 
                    contracted_km, 
                    monthly_subscription_price, 
                    delivery_location, 
                    has_delivery_insurance 
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?) ''', 
                (
                    data.get('car_id'), 
                    data.get('subscription_start_date'), 
                    data.get('subscription_end_date'), 
                    data.get('subscription_duration_months', 3), 
                    data.get('km_driven_during_subscription'), 
                    data.get('contracted_km'), 
                    data.get('monthly_subscription_price'), 
                    data.get('delivery_location'), 
                    data.get('has_delivery_insurance', False)
                )
            )

        return [201, {"message": "New subscription added to database"}]

    except sqlite3.Error as e:
        return [500, {"error": str(e)}]
    
def get_subscriptions():
    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            
            cur.execute(f'SELECT * FROM {TABLE_NAME}')
            data = cur.fetchall()
            
            if not data:
                return [404, {"message": "Subscriptions not found"}]
                    
            return [200, [dict(row) for row in data]]

    except sqlite3.Error as e:
        return [500, {"error": str(e)}]
    
def get_subscription_by_id(id):
    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            
            cur.execute(f'SELECT * FROM {TABLE_NAME} WHERE subscription_id = ?', (id,))
            data = cur.fetchone()
            
            if not data:
                return [404, {"message": "Subscriptions not found"}]
                    
            return [200, dict(data)]

    except sqlite3.Error as e:
        return [500, {"error": str(e)}]

def get_active_subscriptions():
    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()

            # Get today's date in ISO format 
            today = datetime.now().strftime('%Y-%m-%d')
            
            cur.execute(
                f''' SELECT * FROM {TABLE_NAME} 
                WHERE subscription_start_date <= ? 
                AND subscription_end_date >= ? ''', 
                (today, today)
            )
            data = cur.fetchall()
            
            if not data:
                return [404, {"message": "Currently, there are no active subscriptions"}]
                    
            return [200, [dict(row) for row in data]]

    except sqlite3.Error as e:
        return [500, {"error": str(e)}]

def get_active_subscriptions_total_price():
    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()

            # Get today's date in ISO format 
            today = datetime.now().strftime('%Y-%m-%d')
            
            cur.execute(
                f''' SELECT SUM(monthly_subscription_price) as total_price
                FROM {TABLE_NAME} 
                WHERE subscription_start_date <= ? 
                AND subscription_end_date >= ? ''', 
                (today, today)
            )
            data = cur.fetchone()[0]
            
            if not data:
                return [404, {"message": "Currently, there are no active subscriptions"}]
                    
            return [200, {"total_price": data}]

    except sqlite3.Error as e:
        return [500, {"error": str(e)}]

def update_subscription(id, data):
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cur = conn.cursor()
            
            query = f'''
            UPDATE {TABLE_NAME}
            SET '''

            i = 0
            for key,value in data.items():
                if key not in query:
                    if i > 0:
                        query+= ", "

                    if isinstance(value, str):
                        query += f'{key} = "{value}"'
                    else:
                        query += f'{key} = {value}'
                    i += 1

            query += f" WHERE subscription_id = {id}"
            print(query)

            cur.execute(query)
            if cur.rowcount == 0:
                return [404, {"message": "Subscription not found."}]
            
            return [201, {"message": "Subscription updated successfully."}]

    except sqlite3.Error as e:
        return [500, {"error": str(e)}]

def delete_item_by_id(id):
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cur = conn.cursor()

            # Delete the row with the specified id
            cur.execute(f'DELETE FROM {TABLE_NAME} WHERE subscription_id = ?', (id,))
            
            if cur.rowcount == 0:
                return [404, {"message": "Subscription not found."}]
            
            return [200, {"message": f"Subscription deleted from {TABLE_NAME} successfully."}]

    except sqlite3.Error as e:
        return [500, {"error": str(e)}]