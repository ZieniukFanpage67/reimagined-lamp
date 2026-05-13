from fastapi.testclient import TestClient
import pytest
import sqlite3

from app import app, get_db

@pytest.fixture()
def test_db():
    con = sqlite3.connect(":memory:", check_same_thread=False)
    con.executescript("""CREATE TABLE Items(product_id INT NOT NULL PRIMARY KEY, product_name VARCHAR(99), quantity_available int, price float);
                      
                      CREATE TABLE "Orders" (
                            "order_id"	INT NOT NULL,
                            "client_id"	int,
                            "product_id"	int,
                            "quantity"	int,
                            "total_amount_paid"	float NOT NULL,
                            "created_at"	date,
                            "status"	TEXT,
                            "payment_method"	TEXT,
                            FOREIGN KEY("product_id") REFERENCES "Items"("product_id")
                        );
                      
                    INSERT INTO Items ("product_id", "product_name", "quantity_available", "price") VALUES (591268, 'Smartfon APPLE iPhone 15 5G 128GB 6.1 cali Czarny', 19, 3048);
                    INSERT INTO Items ("product_id", "product_name", "quantity_available", "price") VALUES (2013312, 'Słuchawki dokanałowe OPPO Enco AIR4 Pro ANC Biały', 31, 218.92);
                    INSERT INTO Items ("product_id", "product_name", "quantity_available", "price") VALUES (598469, 'Zegarek sportowy GARMIN Vivoactive 5 Czarny', 52, 699);
                    INSERT INTO Items ("product_id", "product_name", "quantity_available", "price") VALUES (2052215, 'Smartfon MOTOROLA Edge 60 5G 12/512GB 6.67" 120Hz Zielony', 32, 1599);
                    INSERT INTO Items ("product_id", "product_name", "quantity_available", "price") VALUES (497870, 'Powerbank XLINE XPB110G 10000 mAh 15W Szary', 44, 89.99);
                    INSERT INTO Orders VALUES (1, 343434, 2013312, 2, 437.84, '2025-04-30',NULL,NULL);
                    INSERT INTO Orders VALUES (1, 343434, 497870, 3, 269.97, '2025-04-30',NULL,NULL);
                    INSERT INTO Orders VALUES (1, NULL, NULL, NULL, 707.81, NULL,'Pending',NULL);

                      """)
    yield con
    con.close()
    

@pytest.fixture()
def client(test_db):
    def override_get_db():
        try:
            yield test_db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()



def test_read_main(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"Hello": "World"}

def test_create_order_success(client):
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

def test_create_order_failure(client):
    payload = {
        "client_id":999,
        "product_id":[598469],
        "quantity":[999]
    }
    
    response = client.post("/orders", json=payload)
    assert response.status_code == 400

def test_read_order(client):
    response = client.get("/orders/1")
    print(response.json())
    assert response.status_code == 200
    data = response.json()
    assert data["OrderID"] == 1



def test_read_order_not_found(client):
    response = client.get("/orders/999")
    assert response.status_code == 404

def test_add_item_success(client):
    payload = {
    "ProductID": 123456,
    "ProductName": "Testowy produkt",
    "QuantityAvailable": 50,
    "Price": 49.99
    }

    response = client.post("/add_item", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["ProductID"] == 123456

def test_add_item_failure(client):
    payload = {
    "ProductID": 123456,
    "ProductName": "Testowy produkt",
    "QuantityAvailable": -50, 
    "Price": 49.99
    }

    response = client.post("/add_item", json=payload)
    assert response.status_code == 500

def test_delete_item_success(client):
    response = client.post("/delete_item/598469")
    assert response.status_code == 200

def test_delete_item_failure(client):
    response = client.post("/delete_item/999999999999")
    assert response.status_code == 404

def test_pay_for_order_success(client):
    payload = {
        "order_id":1,
        "payment_method":'Karta'
    }

    response = client.post("/orders/pay", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["OrderID"] == 1
    assert data["PaymentMethod"] == "Karta"

def test_pay_for_order_failure(client):
    payload = {
        "order_id":999,
        "payment_method":'Karta'
    }

    response = client.post("/orders/pay", json=payload)
    assert response.status_code == 404