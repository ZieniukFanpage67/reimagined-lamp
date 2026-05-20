import React from 'react';
import './App.css';
import Orders from './pages/Orders';
import ProductList from "./components/Products";
import Header from "./components/Header";
import { Route, Routes, useNavigate } from "react-router-dom";
import PlaceOrder from './pages/PlaceOrder';

const App = () => {
  return (
    <div>
      <Header />
      <Routes>
        <Route path='/' element={<ProductList />} />
        <Route path='/placeorder' element={<PlaceOrder />} />
        <Route path='/orders' element={<Orders />} />
      </Routes>
    </div>
  );
};

export default App;
