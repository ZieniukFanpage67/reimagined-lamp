import React, { useEffect, useState } from 'react'
import api from "../api.js";

function ProductList() {
  const [products, setProducts] = useState([]);


  const fetchProducts = async () => {
    try {
      const response = await api.get('/products');
      setProducts(response.data.Products)
    } catch (error) {
      console.error("Error fetching products", error)
    }
  };

  useEffect(() => {
    fetchProducts();
  }, []);


  return (
    <div>
        <br />
        <h2>Produkty</h2>
        <br />
        <div className='justify-center flex'>
            <table>
                <tbody><tr>
                    <th>ID produktu</th>
                    <th>Nazwa produktu</th>
                    <th>Dostępna ilość</th>
                    <th>Cena</th>
                </tr>
                {products.map((product, index) => (
                    <tr>
                        <td key={index}>{product.ProductID}</td>
                        <td key={index}>{product.ProductName}</td>
                        <td key={index}>{product.QuantityAvailable}</td>
                        <td key={index}>{product.Price}zł</td>
                    </tr>
                ))}</tbody>
            </table>
        </div>
    </div>
  )
}

export default ProductList;
