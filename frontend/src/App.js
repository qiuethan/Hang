import React, { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import {useDispatch, useSelector} from "react-redux";

import {debounce} from "lodash";

import Box from "@mui/material/Box";
import CssBaseline from "@mui/material/CssBaseline";

import {connectRTWS, pingRTWS} from "./actions/notifications";

import './App.css';
import Home from './components/Home/Home';
import Auth  from './components/Auth/Auth';
import Navbar from './components/Navbar/Navbar';
import Chat from './components/Chat/Chat';
import Verify from './components/Verify/Verify';
import Friends from './components/Friends/Friends';
import Hang from './components/Hang/Hang';



const App = () => {

  const [currentPage, setCurrentPage] = useState();

  const dispatch = useDispatch();

  const connection = useSelector(state => state.rtws);

  useEffect(() => {
    dispatch(connectRTWS());
    console.log(connection);
  }, [])

  setInterval(() => {
    dispatch(pingRTWS)
  }, 10000);

  connection.onmessage = (message) => {
    try{
      const m = JSON.parse(message.data);
      if(m.type === "status" && m.message === "success"){
        console.log("True");
      }
    }
    catch(error){
      console.log(error);
    }

  }

  return (
    <BrowserRouter>
      <Box sx={{ display:"flex", height:'100vh', width:'100vw'}}>
        <CssBaseline/>
        <Navbar setCurrentPage={setCurrentPage}/>
        <Box sx={{ flexGrow : 1 }}>
          <Routes>
            <Route path="/" element={<Home currentPage={currentPage} setCurrentPage={setCurrentPage}/>}/>
            <Route path="/auth" element={<Auth currentPage={currentPage} setCurrentPage={setCurrentPage} />}/>
            <Route path="/chat" element={<Chat currentPage={currentPage} setCurrentPage={setCurrentPage}/>}/>
            <Route path="/friends" element={<Friends currentPage={currentPage} setCurrentPage={setCurrentPage}/>}/>
            <Route path="/hang/*" element={<Hang currentPage={currentPage} setCurrentPage={setCurrentPage}/>}/>
            <Route path="/verify" element={<Verify/>}/>
          </Routes> 
        </Box>
      </Box>
    </BrowserRouter>
  );
}

export default App;
