from fastapi.testclient import TestClient

from app import app

client = TestClient(app)

def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"Hello": "World"}

def test_read_order():
    response = client.get("/orders/1")
    assert response.status_code == 200
    data = response.json()
    assert data["OrderID"] == 1

def test_create_order_success():
    payload = {
        "client_id":999,
        "product_id":[598469],
        "quantity":[1]
    }
    
    response = client.post("/orders", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert data["ClientID"]==999
    assert data["ProductID"]==[598469]
    assert data["QuantityOrdered"]==[1]
    assert data["TotalAmountPaid"]==699.0

def test_create_order_failure():
    payload = {
        "client_id":999,
        "product_id":[598469],
        "quantity":[999]
    }
    
    response = client.post("/orders", json=payload)
    assert response.status_code == 400

def test_read_order_not_found():
    response = client.get("/orders/999")
    assert response.status_code == 404

