import React from 'react';

import './App.css';
import Home from './components/Home/Home';
import Auth  from './components/Auth/Auth';
import Navbar from './components/Navbar/Navbar';
import Chat from './components/Chat/Chat';
import { BrowserRouter, Routes, Route } from 'react-router-dom';

const App = () => {
  return (
    <BrowserRouter>
      <div>
        <Navbar/>
        <Routes>
          <Route path="/" element={<Home/>}/>
          <Route path="/auth" element={<Auth/>}/>
          <Route path="/chat" element={<Chat/>}/>
        </Routes>
      </div>
    </BrowserRouter>
  );
}

export default App;
