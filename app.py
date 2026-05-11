import sqlite3
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
import datetime

app = FastAPI()

class Order(BaseModel):
    client_id: int
    product_id: list[int]
    quantity: list[int]

class ProductInfo(BaseModel):
    ProductID: int
    ProductName: str
    QuantityOrdered: int
    Price: float

class OrderInfo(BaseModel):
    OrderID: int
    ClientID: int
    Products: list[ProductInfo]
    TotalAmountPaid: float
    OrderedAt: str

class PlacedOrder(BaseModel):
    OrderID: int
    ClientID: int
    ProductID: list[int]
    QuantityOrdered: list[int]
    TotalAmountPaid: float
    OrderedAt: str



@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/orders/{order_id}")
def read_order_info(order_id: int) -> OrderInfo:
    con = sqlite3.connect("./orders.db")
    cur = con.cursor()
    final_price = 0
    cur.execute("SELECT * FROM Orders WHERE order_id = ?", (order_id,))
    order_info = cur.fetchall()
    if (order_info != []):
        products = []
        for i in range(len(order_info)):
            if order_info[i][1]==None:
                final_price = order_info[i][4]
            else:
                cur.execute("SELECT product_name FROM Items where product_id = ?", (order_info[i][2],))
                productname = cur.fetchone()[0]
                products.append({
                    "ProductID":order_info[i][2],
                    "ProductName":productname,
                    "QuantityOrdered":order_info[i][3],
                    "Price":order_info[i][4]
                })
        con.close()
        return {"OrderID":order_info[0][0],
                "ClientID":order_info[0][1],
                "Products":products,
                "TotalAmountPaid":final_price,
                "OrderedAt":order_info[0][5]
                }
    else:
        con.close()
        raise HTTPException(status_code=404, detail="Order not found in database")
    
@app.post("/orders")
async def place_order(orderinfo: Order) -> PlacedOrder:
    con = sqlite3.connect("./orders.db")
    cur = con.cursor()
    final_amount = 0
    are_all_products_available = True
    cur.execute("SELECT order_id FROM Orders order by order_id DESC")
    currentid = int(cur.fetchone()[0])
    if currentid <= 0:
        newid = 1
    else:
        newid = currentid + 1
    for j in range(len(orderinfo.quantity)):
        cur.execute("SELECT quantity_available FROM Items WHERE product_id = ?", (orderinfo.product_id[j],))
        if (int(cur.fetchone()[0]) >= orderinfo.quantity[j]):
            are_all_products_available = True
        else:
            con.close()
            are_all_products_available = False
            raise HTTPException(status_code=400, detail="Produkt nie jest aktualnie dostępny")
    if are_all_products_available == True:
        for i in range(len(orderinfo.product_id)):
            cur.execute("UPDATE Items SET quantity_available=(quantity_available-?) WHERE product_id = ?", (orderinfo.quantity[i],orderinfo.product_id[i]))
            cur.execute("SELECT price FROM Items WHERE product_id = ?", (orderinfo.product_id[i],))
            total_amount_paid = cur.fetchone()[0] * orderinfo.quantity[i]
            final_amount += total_amount_paid
            created_at = datetime.datetime.now().strftime("%c")
            cur.execute("INSERT INTO Orders VALUES (?,?,?,?,?,?)",(newid,orderinfo.client_id, orderinfo.product_id[i], orderinfo.quantity[i], total_amount_paid, created_at))
            con.commit()
    final_amount2 = round(final_amount,2)
    cur.execute("INSERT INTO Orders VALUES (?,?,?,?,?,?)",(newid,None,None,None, final_amount2, None))
    con.commit()
    con.close()
    return {"OrderID": newid,
            "ClientID":orderinfo.client_id,
            "ProductID":orderinfo.product_id,
            "QuantityOrdered":orderinfo.quantity,
            "TotalAmountPaid":final_amount2,
            "OrderedAt": created_at
            }


# test2
    

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info", reload=False)