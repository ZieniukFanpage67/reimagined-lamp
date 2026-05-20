import React from 'react';
import { Link } from "react-router-dom";

const Header = () => {
  return (
    <header className='sticky top-0 bg-violet-400 p-4 text-amber-50 grid grid-flow-col justify-items-center text-shadow-lg font-bold'>
        <Link to="/">Produkty</Link>
        <Link to="/placeorder">Zamów</Link>
        <Link to="/orders">Sprawdź zamówienie</Link>
    </header>
  );
};

export default Header;