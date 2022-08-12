import React, { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';

import './App.css';
import Home from './components/Home/Home';
import Auth  from './components/Auth/Auth';
import Navbar from './components/Navbar/Navbar';
import Chat from './components/Chat/Chat';
import Verify from './components/Verify/Verify';
import Friends from './components/Friends/Friends';

import Box from "@mui/material/Box";
import CssBaseline from "@mui/material/CssBaseline";

const App = () => {

  const [currentPage, setCurrentPage] = useState();

  return (
    <BrowserRouter>
      <Box sx={{ display : "flex"}}>
        <CssBaseline/>
        <Navbar setCurrentPage={setCurrentPage}/>
        <Box sx={{ flexGrow : 1, p:3 }}>
          <Routes>
            <Route path="/" element={<Home currentPage={currentPage} setCurrentPage={setCurrentPage}/>}/>
            <Route path="/auth" element={<Auth currentPage={currentPage} setCurrentPage={setCurrentPage} />}/>
            <Route path="/chat" element={<Chat currentPage={currentPage} setCurrentPage={setCurrentPage}/>}/>
            <Route path="/friends" element={<Friends currentPage={currentPage} setCurrentPage={setCurrentPage}/>}/>
            <Route path="/verify" element={<Verify/>}/>
          </Routes> 
        </Box>
      </Box>
    </BrowserRouter>
  );
}

export default App;
