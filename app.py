import sqlite3
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
import uvicorn
import datetime
from enum import Enum

app = FastAPI()


def get_db():
    con = sqlite3.connect("orders.db", check_same_thread=False)
    try:
        yield con
    finally:
        con.close()

class OrderStatus(Enum):
    PENDING = "Pending"
    PAID = "Paid"

class PaymentMethod(Enum):
    CASH = "Gotówka"
    CARD = "Karta"

class Payments(BaseModel):
    PaymentMethod: PaymentMethod
    AmountPaid: float

class PayForOrderResponse(BaseModel):
    OrderID: int
    Payments: list[Payments]
    TotalAmountPaid: float

class PayForOrderRequest(BaseModel):
    order_id: int
    payment_method: list[PaymentMethod]
    amount_to_pay: list[float]

class Order(BaseModel):
    client_id: int
    product_id: list[int]
    quantity: list[int]

class ProductInfo(BaseModel):
    ProductID: int
    ProductName: str
    QuantityOrdered: int
    Price: float

class NewProduct(BaseModel):
    ProductID: int
    ProductName: str
    QuantityAvailable: int
    Price: float

class OrderInfo(BaseModel):
    OrderID: int
    ClientID: int
    Products: list[ProductInfo]
    TotalAmountPaid: float
    OrderedAt: str
    Status: OrderStatus
    PaymentMethod: str

class PlacedOrder(BaseModel):
    OrderID: int
    ClientID: int
    ProductID: list[int]
    QuantityOrdered: list[int]
    TotalAmountPaid: float
    OrderedAt: str
    Status: OrderStatus



@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/orders/{order_id}")
def read_order_info(order_id: int, db = Depends(get_db)) -> OrderInfo:
    cur = db.cursor()
    final_price = 0
    cur.execute("SELECT * FROM Orders WHERE order_id = ?", (order_id,))
    order_info = cur.fetchall()
    if (order_info != []):
        products = []
        for i in range(len(order_info)):
            if order_info[i][1]==None:
                final_price = order_info[i][4]
                status = order_info[i][6]
                paymentmethod = order_info[i][7]
            else:
                cur.execute("SELECT product_name FROM Items where product_id = ?", (order_info[i][2],))
                productname = cur.fetchone()[0]
                products.append({
                    "ProductID":order_info[i][2],
                    "ProductName":productname,
                    "QuantityOrdered":order_info[i][3],
                    "Price":round(order_info[i][4],2)
                })
        paymentmethod2 = None
        for s in PaymentMethod:
            if (paymentmethod == s.name):
                paymentmethod2 = s.value

        if paymentmethod2 is None:
            paymentmethod2 = "Nieopłacone"

        return {"OrderID":order_info[0][0],
                "ClientID":order_info[0][1],
                "Products":products,
                "TotalAmountPaid":final_price,
                "OrderedAt":order_info[0][5],
                "Status":status,
                "PaymentMethod": paymentmethod2
                }
    else:
        raise HTTPException(status_code=404, detail="Order not found in database")
    
@app.post("/orders")
async def place_order(orderinfo: Order, db = Depends(get_db)) -> PlacedOrder:
    cur = db.cursor()
    final_amount = 0
    are_all_products_available = True
    cur.execute("SELECT order_id FROM Orders order by order_id DESC")
    row = cur.fetchone()
    currentid = row[0] if row else 0
    newid = currentid + 1
    for j in range(len(orderinfo.quantity)):
        cur.execute("SELECT quantity_available FROM Items WHERE product_id = ?", (orderinfo.product_id[j],))
        if (int(cur.fetchone()[0]) >= orderinfo.quantity[j]):
            are_all_products_available = True
        else:
            are_all_products_available = False
            raise HTTPException(status_code=400, detail="Produkt nie jest aktualnie dostępny")
    if are_all_products_available == True:
        for i in range(len(orderinfo.product_id)):
            cur.execute("UPDATE Items SET quantity_available=(quantity_available-?) WHERE product_id = ?", (orderinfo.quantity[i],orderinfo.product_id[i]))
            cur.execute("SELECT price FROM Items WHERE product_id = ?", (orderinfo.product_id[i],))
            total_amount_paid = cur.fetchone()[0] * orderinfo.quantity[i]
            final_amount += total_amount_paid
            created_at = datetime.datetime.now().strftime("%c")
            cur.execute("INSERT INTO Orders VALUES (?,?,?,?,?,?,?,?)",(newid,orderinfo.client_id, orderinfo.product_id[i], orderinfo.quantity[i], total_amount_paid, created_at, None, None))
    final_amount2 = round(final_amount,2)
    cur.execute("INSERT INTO Orders VALUES (?,?,?,?,?,?,?,?)",(newid,None,None,None, final_amount2, None, str(OrderStatus.PENDING.value), None))
    db.commit()
    return {"OrderID": newid,
            "ClientID":orderinfo.client_id,
            "ProductID":orderinfo.product_id,
            "QuantityOrdered":orderinfo.quantity,
            "TotalAmountPaid":final_amount2,
            "OrderedAt": created_at,
            "Status": OrderStatus.PENDING
            }


@app.post("/add_item")
async def add_item(productinfo: NewProduct, db = Depends(get_db)) -> NewProduct:
    cur = db.cursor()
    if ((productinfo.QuantityAvailable <= 0) or (round(productinfo.Price,2) <= 0)):
        raise HTTPException(status_code=500, detail="Quantity or price can't be lower than 0")
    else:
        cur.execute("SELECT product_id from Items WHERE product_id = ?", (productinfo.ProductID,))
        if (cur.fetchall() == []):
            cur.execute("INSERT INTO Items VALUES (?,?,?,?)", (productinfo.ProductID, productinfo.ProductName, productinfo.QuantityAvailable, productinfo.Price))
            db.commit()
            return productinfo
        else:
            raise HTTPException(status_code=500, detail="Product already exists in the database")

@app.post("/delete_item/{product_id}")
async def delete_item(product_id: int, db = Depends(get_db)):
    cur = db.cursor()
    cur.execute("SELECT product_id from Items WHERE product_id = ?", (product_id,))
    if (cur.fetchall() == []):
        raise HTTPException(status_code=404, detail="Product doesn't exist in the database")
    else:
        cur.execute("DELETE FROM Items WHERE product_id = ?", (product_id,))
        db.commit()
        return {f"Successfully deleted item {product_id}"}
    
@app.post("/orders/pay")
async def pay_for_order(req: PayForOrderRequest, db = Depends(get_db)) -> PayForOrderResponse:
    cur = db.cursor()
    paymentsstr = ""
    payments = []
    price_check = 0
    if (len(req.payment_method) > 2) or (len(req.amount_to_pay) > 2):
        raise HTTPException(status_code=500, detail="There can't be more than 2 payment methods")
    else:
        cur.execute("SELECT * from Orders WHERE order_id = ?", (req.order_id,))
        order_info = cur.fetchall()
        if (order_info != []):
            for i in range(len(order_info)):
                if order_info[i][1]==None:
                    final_price = order_info[i][4]
                    status = order_info[i][6]
        else:
            raise HTTPException(status_code=404, detail="Order not found in database")
        if (status == "Paid"):
            raise HTTPException(status_code=500, detail="Order already paid for")
        else:
            for j in range(len(req.payment_method)):
                price_check += abs(req.amount_to_pay[j])
                payments.append({
                    "PaymentMethod": req.payment_method[j],
                    "AmountPaid": abs(req.amount_to_pay[j])
                })
            if (round(price_check,2) == round(final_price,2)):
                if (len(req.payment_method) == 2):
                    if (req.payment_method[0] == req.payment_method[1]):
                        raise HTTPException(status_code=500, detail="Can't have two same payment methods")
                    else:
                        paymentsstr = "CARD + CASH"
                else:
                    paymentsstr = str(req.payment_method[0].name)
                cur.execute("UPDATE Orders SET status = 'Paid', payment_method = ? WHERE (order_id = ?) and (client_id IS NULL)", (paymentsstr,req.order_id,))
                db.commit()
                return {"OrderID": req.order_id,
                        "Payments" : payments,
                        "TotalAmountPaid": round(final_price,2)}
            else:
                raise HTTPException(status_code=500, detail="You need to pay the full price")
    
    

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info", reload=False)