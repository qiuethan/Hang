import React, { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import {useDispatch, useSelector} from "react-redux";

import {debounce} from "lodash";

import Box from "@mui/material/Box";
import CssBaseline from "@mui/material/CssBaseline";

import {connectRTWS, getUnreadNotifications} from "./actions/notifications";
import {gethangevents} from "./actions/hang";
import {loadblockedusers, loadfriends, loadrecievedfriendrequests, loadsentfriendrequests} from "./actions/friends";

import './App.css';
import Home from './components/Home/Home';
import Auth  from './components/Auth/Auth';
import Navbar from './components/Navbar/Navbar';
import Chat from './components/Chat/Chat';
import Verify from './components/Verify/Verify';
import Friends from './components/Friends/Friends';
import Hang from './components/Hang/Hang';
import Profile from './components/Profile/Profile';

const App = () => {

  const [currentPage, setCurrentPage] = useState();
  const [wsConnected, setWsConnected] = useState(false);

  const dispatch = useDispatch();

  const connection = useSelector(state => state.rtws);

  const ping = () => {
    if(wsConnected){
      try{
        connection.send(
            JSON.stringify(
                {
                  action: "ping",
                  content: {}
                }
            )
        )
      }
      catch(error){
        console.log(error);
        setWsConnected(false);
        connectRTWS();
      }
    }
  }

  setInterval(ping, 10000);

  useEffect(() => {
    const connect = async() => {
      const status = await dispatch(connectRTWS());
    }

    connect();
  }, [])

  try{
    connection.onmessage = (message) => {
      try{
        const m = JSON.parse(message.data);
        try{
          if(m.type === "status" ){
            if(m.message === "success"){
              setWsConnected(true);
            }
          }
          if(m.type === "update"){
            dispatch(getUnreadNotifications());
            if(m.content === "hang_event"){
              dispatch(gethangevents());
            }
            if(m.content === "friend_request"){
              dispatch(loadrecievedfriendrequests());
              dispatch(loadsentfriendrequests());
              dispatch(loadblockedusers());
            }
            if(m.content === "friends"){
              dispatch(loadfriends());
            }
            if(m.content === "chat"){

            }
          }
        }
        catch(error){
          console.log(error);
        }
      }
      catch(error){
        console.log(error);
      }

    }
  }
  catch (error){
    console.log(error);
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
            <Route path="/profile" element={<Profile currentPage={currentPage} setCurrentPage={setCurrentPage}/>}/>
            <Route path="/verify" element={<Verify/>}/>
          </Routes> 
        </Box>
      </Box>
    </BrowserRouter>
  );
}

export default App;
