/*
Author: Ethan Qiu
Filename: Chat.js
Last Modified: June 7, 2023
Description: Overall chat component
*/

import React, { useEffect, useState } from 'react';
import Chatroom from './Chatroom/Chatroom';
import Chatlist from './Chatlist/Chatlist';
import { useDispatch, useSelector } from 'react-redux';
import { connectws } from '../../actions/chat';
import { useNavigate } from 'react-router-dom';
import Grouplist from './Chatlist/Grouplist';
import { Grid, Box } from '@mui/material';

// Handles the chat feature.
const Chat = ({ currentPage, setCurrentPage }) => {

    // Setting up local state using useState hook
    const [currentRoom, setCurrentRoom] = useState(); // Keeps track of the current chat room
    const [clientOpened, setClientOpened] = useState(false); // Track if the client has opened connection

    // useSelector to access state from the Redux store.
    const client = useSelector(state => state.websocket); // Access websocket from Redux store

    // Setting up Redux's useDispatch hook to dispatch actions.
    const dispatch = useDispatch();

    // Setting up the react-router-dom hook to navigate between pages.
    const navigate = useNavigate();

    // Using useEffect hook to perform side-effects.
    useEffect(() => {
        setCurrentPage("chat");
        if(JSON.parse(localStorage.getItem('profile')) == null){
            navigate("/auth") // If there is no user profile in local storage, redirect to authentication page
        }
        dispatch(connectws()); // Dispatching an action to connect websocket
    }, [currentPage]);

    // Try to open a websocket connection and authenticate the user.
    try{
        client.onopen = () => {
            client.send(JSON.stringify({
                action: "authenticate",
                content: {
                    token: JSON.parse(localStorage.getItem('profile')).token
                }
            }));
            setClientOpened(true); // When connection opens set the clientOpened state to true
        }
    }
    catch (error){
        console.log(error); // Log any error during connection open
    }

    // If the websocket connection closes, set clientOpened to false.
    try{
        client.onclose = () => {
            setClientOpened(false);
        }
    }
    catch (error){
        console.log(error); // Log any error during connection close
    }

    // Rendering chat UI
    return(
        <Box sx={{display: "flex", height: '100%', width: '100%', alignItems: "center", justifyContent: "center"}}>
            <Grid sx={{display: "flex", flexDirection: "row", height: "96%", width: "98%"}} container>
                <Grid sx={{display: "flex", flexDirection: "column", height: "100%", width: "100%"}} item xs={2}>
                    <Chatlist client={client} currentRoom={currentRoom} setCurrentRoom={setCurrentRoom} clientOpened={clientOpened}/>
                    <Grouplist client={client} currentRoom={currentRoom} setCurrentRoom = {setCurrentRoom} clientOpened={clientOpened}/>
                </Grid>
                <Grid sx={{display: "flex", height: "100%", width: "100%", justifySelf: "flex-end"}} item xs={10}>
                    <Chatroom client={client} currentRoom={currentRoom} clientOpened={clientOpened} setClientOpened={setClientOpened}/>
                </Grid>
            </Grid>
        </Box>
    );
}

export default Chat;