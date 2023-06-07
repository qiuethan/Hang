/*
Author: Ethan Qiu
Filename: App.js
Last Modified: June 7, 2023
Description: File where all components are housed
*/


import React, { useState, useEffect } from 'react';
import {BrowserRouter, Routes, Route} from 'react-router-dom';
import {useDispatch, useSelector} from "react-redux";

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
import {connectws} from "./actions/chat";

//App Component
const App = () => {

  //Define currentPage state variable
  const [currentPage, setCurrentPage] = useState();

  //Define wsConected state variable
  const [wsConnected, setWsConnected] = useState(false);

  //Define dispatch variable
  const dispatch = useDispatch();

  //Get real time websocket from react store
  const connection = useSelector(state => state.rtws);

  //On render
  useEffect(() => {
    //Connect chat websocket
    dispatch(connectws());
  }, [])

  //On render
  useEffect(() => {
    //Connect real time webscoket
    const connect = async() => {
      const status = await dispatch(connectRTWS());
    }

    connect();
  }, [])

  try{
    //Response from real time websocket
    connection.onmessage = (message) => {
      try{
        //Get response value
        const m = JSON.parse(message.data);
        try{
          //If status, connected = true
          if(m.type === "status" ){
            if(m.message === "success"){
              setWsConnected(true);
            }
          }
          //If update, update react store via API call
          if(m.type === "update"){
            dispatch(getUnreadNotifications());
            if(m.content === "hang_event"){
              dispatch(gethangevents());
            }
            if(m.content === "friend_request"){
              dispatch(loadfriends());
              dispatch(loadrecievedfriendrequests());
              dispatch(loadsentfriendrequests());
              dispatch(loadblockedusers());
            }
            if(m.content === "friends"){
              dispatch(loadfriends());
              dispatch(loadrecievedfriendrequests());
              dispatch(loadsentfriendrequests());
              dispatch(loadblockedusers());
            }
            if(m.content === "profile"){
              dispatch(loadfriends());
              dispatch(loadrecievedfriendrequests());
              dispatch(loadsentfriendrequests());
              dispatch(loadblockedusers());
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

  //Render components in BrowserRouter
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
