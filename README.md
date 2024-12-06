# Subscriptions Microservice

This microservice provides endpoints to manage subscription-related operations. It includes functionalities to add, update, delete, and retrieve subscriptions.

## Table of Contents
- [API Endpoints](#api-endpoints)
  - [GET /subscriptions](#get-subscriptions)
  - [GET /subscriptions/{id}](#get-subscriptionid)
  - [GET /subscriptions/current](#get-subscriptionscurrent)
  - [GET /subscriptions/current/total-price](#get-subscriptionscurrenttotal-price)
  - [GET /subscriptions/{id}/car](#get-subscriptionidcar)
  - [POST /subscriptions](#post-subscriptions)
  - [PATCH /subscriptions/{id}](#patch-subscriptionid)
  - [DELETE /subscriptions/{id}](#delete-subscriptionid)
- [License](#license)

## API Endpoints

### GET /subscriptions
- **Description**: Retrieve a list of subscriptions (admin role required).
- **Example Request**:
    ```http
    GET /subscriptions
    ```
- **Response**:
    ```json
    [
        {
            "subscription_id": 1,
            "car_id": 101,
            "subscription_start_date": "2024-12-01",
            "subscription_end_date": "2025-12-01",
            "subscription_duration_months": 12,
            "km_driven_during_subscription": 15000,
            "contracted_km": 20000,
            "monthly_subscription_price": 26500,
            "delivery_location": "Copenhagen",
            "has_delivery_insurance": true
        },
        ...
    ]
    ```
- **Response Codes**: `200`, `400`, `500`

### GET /subscriptions/{id}
- **Description**: Retrieve a specific subscription by ID (admin role required).
- **Example Request**:
    ```http
    GET /subscriptions/1
    ```
- **Response**:
    ```json
    {
        "subscription_id": 1,
        "car_id": 101,
        "subscription_start_date": "2024-12-01",
        "subscription_end_date": "2025-12-01",
        "subscription_duration_months": 12,
        "km_driven_during_subscription": 15000,
        "contracted_km": 20000,
        "monthly_subscription_price": 26500,
        "delivery_location": "Copenhagen",
        "has_delivery_insurance": true
    }
    ```
- **Response Codes**: `200`, `400`, `404`, `500`

### GET /subscriptions/current
- **Description**: Retrieve a list of current active subscriptions (admin role required).
- **Example Request**:
    ```http
    GET /subscriptions/current
    ```
- **Response**:
    ```json
    [
        {
            "subscription_id": 1,
            "car_id": 101,
            "subscription_start_date": "2024-12-01",
            "subscription_end_date": "2025-12-01",
            "subscription_duration_months": 12,
            "km_driven_during_subscription": 15000,
            "contracted_km": 20000,
            "monthly_subscription_price": 26500,
            "delivery_location": "Copenhagen",
            "has_delivery_insurance": true
        },
        ...
    ]
    ```
- **Response Codes**: `200`, `400`, `404`, `500`

### GET /subscriptions/current/total-price
- **Description**: Retrieve the total price of current active subscriptions (admin role required).
- **Example Request**:
    ```http
    GET /subscriptions/current/total-price
    ```
- **Response**:
    ```json
    {
        "total_price": 599.98
    }
    ```
- **Response Codes**: `200`, `400`, `404`, `500`

### GET /subscriptions/{id}/car
- **Description**: Retrieve car information for a specific subscription by ID (admin role required).
- **Example Request**:
    ```http
    GET /subscriptions/1/car
    ```
- **Response**:
    ```json
    {
        "car_info": "Car information goes here"
    }
    ```
- **Response Codes**: `200`, `400`, `404`, `500`

### POST /subscriptions
- **Description**: Add a new subscription (admin role required).
- **Example Request**:
    ```http
    POST /subscriptions
    Content-Type: application/json

    {
        "car_id": 101,
        "subscription_start_date": "2024-12-01",
        "subscription_end_date": "2025-12-01",
        "subscription_duration_months": 12,
        "km_driven_during_subscription": 15000,
        "contracted_km": 20000,
        "monthly_subscription_price": 26500,
        "delivery_location": "Copenhagen",
        "has_delivery_insurance": true
    }
    ```
- **Response**:
    ```json
    {
        "message": "New subscription added to database"
    }
    ```
- **Response Codes**: `201`, `400`, `500`

### PATCH /subscriptions/{id}
- **Description**: Update an existing subscription (admin role required).
- **Example Request**:
    ```http
    PATCH /subscriptions/1
    Content-Type: application/json

    {
        "subscription_end_date": "2025-11-30",
        "subscription_duration_months": 11
    }
    ```
- **Response**:
    ```json
    {
        "message": "Subscription updated successfully."
    }
    ```
- **Response Codes**: `201`, `400`, `404`, `500`

### DELETE /subscriptions/{id}
- **Description**: Delete a subscription by ID (admin role required).
- **Example Request**:
    ```http
    DELETE /subscriptions/1
    ```
- **Response**:
    ```json
    {
        "message": "Subscription deleted from subscriptions successfully."
    }
    ```
- **Response Codes**: `200`, `400`, `404`, `500`

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.