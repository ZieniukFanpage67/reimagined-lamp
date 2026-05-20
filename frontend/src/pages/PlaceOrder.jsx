import React, { useState, useEffect } from 'react';
import api from "../api.js";

const PlaceOrder = () => {
    const [clientid, setClientid] = useState(0);
    const [productid, setProductid] = useState(0);
    const [quantity, setQuantity] = useState(0);
    const [products, setProducts] = useState([]);
    const [fetchedproducts, setFetchedproducts] = useState([]);
    const [successfullyadded, setSuccess] = useState(false)

    const fetchProducts = async () => {
    try {
      const response = await api.get('/products');
      setFetchedproducts(response.data.Products)
    } catch (error) {
      console.error("Error fetching products", error)
    }
  };
    
    
    const add_product = () => {
        try {
            if (products.some(i => i.productid === productid)){
                console.error("WONG WONG WONG")
            } else {
                if(fetchedproducts.some(i => i.ProductID === productid)){
                    const result = fetchedproducts.filter(i => i.ProductID === productid)
                    const productname = result[0].ProductName
                    setProducts([...products, {productid,productname,quantity}]);
                } else {
                    console.error("DIS IS VERI WONG")
                }
            }
        } catch (error) {
            console.error("sum ting wong", error)
        }
    }

    

    const handleSubmit = async (event) => {
        event.preventDefault();
        try {
            const productidlist = []
            const quantitylist = []
            products.forEach(i => {
                productidlist.push(i.productid)
                quantitylist.push(i.quantity)
            })
            const payload = {
                "client_id": clientid,
                "product_id": productidlist,
                "quantity": quantitylist
            }

            await api.post('/orders', payload)
            setSuccess(true)
        } catch(error) {
            alert(error)
        }
    }

    useEffect(() => {
        fetchProducts();
    }, []);

    return (
        <div className='p-8'>
            <form onSubmit={handleSubmit}>
                <label>ID klienta: </label>
                <input type='number' value={clientid} onChange={(e) => setClientid(parseInt(e.target.value))} className='bg-white text-black'></input><br /><br />
                <label>ID produktu: </label>
                <input type='number' value={productid} onChange={(e) => setProductid(parseInt(e.target.value))} className='bg-white text-black'></input><br /><br />
                <label>Ilość: </label>
                <input type='number' value={quantity} onChange={(e) => setQuantity(parseInt(e.target.value))} className='bg-white text-black'></input><br />
                <div className='p-8'>
                    <button type="button" onClick={add_product} className="bg-violet-500 hover:bg-violet-700 text-white font-bold py-2 px-4 rounded">Dodaj produkt</button>
                    <input type="submit" value={"Złóż zamówienie"} className="bg-violet-500 hover:bg-violet-700 text-white font-bold py-2 px-4 rounded" />
                </div>
            </form>
            <ul>
                {products.map((i,j) => (<li key={j}>{i.productname} {i.productid} x {i.quantity}</li>))}
            </ul>
            {successfullyadded ? <div><h2>Pomyślnie złożono zamówienie</h2></div> : <div></div>}
        </div>
    );
};

export default PlaceOrder;