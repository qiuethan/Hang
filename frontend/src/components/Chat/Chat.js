import React, { useEffect, useState } from 'react';
import { w3cwebsocket as W3CWebSocket } from "websocket";

import Chatroom from './Chatroom/Chatroom';
import Chatlist from './Chatlist/Chatlist';
import { useDispatch, useSelector } from 'react-redux';
import { connectws } from '../../actions/chat';
import { useNavigate } from 'react-router-dom';
import Grouplist from './Chatlist/Grouplist';

import { Grid, Box } from '@mui/material';

const Chat = ({ currentPage, setCurrentPage }) => {

    const [currentRoom, setCurrentRoom] = useState();
    const client = useSelector(state => state.websocket);

    const [clientOpened, setClientOpened] = useState(false);

    const dispatch = useDispatch();

    const navigate = useNavigate();

    useEffect(() => {
        setCurrentPage("chat");
        if(JSON.parse(localStorage.getItem('profile')) == null){
            navigate("/auth")
        }
        dispatch(connectws());
    }, [currentPage]);

    try{
        client.onopen = () => {
            client.send(JSON.stringify({
                action: "authenticate",
                content: {
                    token: JSON.parse(localStorage.getItem('profile')).token
                }
            }));
            setClientOpened(true);
        }
    }
    catch (error){
        console.log(error);
    }
    
    try{
        client.onclose = () => {
            setClientOpened(false);
        }
    }
    catch (error){
        console.log(error);
    }

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