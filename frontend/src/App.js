import React from 'react';

import './App.css';
import Home from './components/Home/Home';
import Auth  from './components/Auth/Auth';
import { BrowserRouter, Routes, Route } from 'react-router-dom';

const App = () => {
  return (
    <BrowserRouter>
      <div>
        <Routes>
          <Route path="/" element={<Home/>}/>
          <Route path="/auth" element={<Auth/>}/>
        </Routes>
      </div>
    </BrowserRouter>
  );
}

export default App;
