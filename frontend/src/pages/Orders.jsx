import React, { useState } from 'react';
import api from "../api.js";

const Orders = () => {
  const [orderid,setOrderid] = useState(0);
  const [orderinfo, setOrderInfo] = useState([]);
  const [showOrderInfo, setShowOrderInfo] = useState(false);

  const fetchOrderInfo = async (event) => {
    event.preventDefault();
    try {
      const response = await api.get('/orders/'+orderid);
      setOrderInfo(response.data);
      setShowOrderInfo(true);
    } catch (error) {
      console.error("Error fetching order info", error)
      alert("Zamówienie nie jest w bazie")
    }
  }


  return (
    <div>
      <br />
      <h2>Sprawdź informacje o zamówieniu</h2>
      <form onSubmit={fetchOrderInfo}>
        <label for="idzamowienia">Numer zamówienia:</label><br />
        <input type='number' id="idzamowienia" name='idzamowienia' value={orderid} onChange={(e) => setOrderid(e.target.value)} placeholder="1234" className='bg-white text-black'></input><br /><br />
        <input type='submit' value={"Sprawdź"} className='bg-white text-black'></input>
      </form>
      <br /><br />
      {showOrderInfo ? <div className='p-8 text-white'>
        <div>
          <div>
            <p className='text-3xl'>Zamówienie nr. {orderinfo.OrderID}:</p>< br/>
            <div className='float-left text-left'>
              <p>ID klienta: {orderinfo.ClientID}</p>
              <p>Data zamówienia: {orderinfo.OrderedAt}</p>
            </div>
            <div className='float-right text-right'>
              <p>Status zamówienia: {orderinfo.Status}</p>
              <p>Metoda płatności: {orderinfo.PaymentMethod}</p>
            </div>
            <br /><br /><br />
          </div>
          <p className='text-3xl text-left'>Zamówione produkty</p>
          <br />
          <hr />
          <br />
          {orderinfo.Products.map((i,j) => (
            <div className='clearfix'>
              <div className='float-left'>
                <p key={j} className='flex justify-start text-xl'>{i.ProductName}</p>
                <p key={j} className='flex justify-start text-gray-300'>{i.ProductID}</p>
              </div>
              <div className='float-right'>
                <p key={j} className='flex justify-end text-xl'>{i.Price} zł</p>
                <p key={j} className='flex justify-end text-gray-300'>Ilość: {i.QuantityOrdered}</p>
              </div>
              <br /><br /><br />
            </div>
          ))}
          <hr /><br />
          <div className='text-3xl float-right flex whitespace-pre'><p className='font-bold'>Łącznie: </p> {orderinfo.TotalAmountPaid} zł</div>
        </div>
      </div> : <div></div>}
    </div>
  );
};

export default Orders;
