import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';

import './App.css';
import Home from './components/Home/Home';
import Auth  from './components/Auth/Auth';
import Navbar from './components/Navbar/Navbar';
import Chat from './components/Chat/Chat';
import Verify from './components/Verify/Verify';
import Friends from './components/Friends/Friends';

const App = () => {
  return (
    <BrowserRouter>
      <div>
        <Navbar/>
        <Routes>
          <Route path="/" element={<Home/>}/>
          <Route path="/auth" element={<Auth/>}/>
          <Route path="/chat" element={<Chat/>}/>
          <Route path="/friends" element={<Friends/>}/>
          <Route path="/verify" element={<Verify/>}/>
        </Routes>
      </div>
    </BrowserRouter>
  );
}

export default App;
