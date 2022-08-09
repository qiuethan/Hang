import React, { useEffect, useState } from 'react';
import { w3cwebsocket as W3CWebSocket } from "websocket";

import Chatroom from './Chatroom/Chatroom';
import Chatlist from './Chatlist/Chatlist';
import { useDispatch, useSelector } from 'react-redux';
import { connectws } from '../../actions/chat';
import { useNavigate } from 'react-router-dom';
import Grouplist from './Chatlist/Grouplist';

const Chat = () => {

    const [currentRoom, setCurrentRoom] = useState();
    const client = useSelector(state => state.websocket);

    const [clientOpened, setClientOpened] = useState(false);

    const dispatch = useDispatch();

    const navigate = useNavigate();

    useEffect(() => {
        if(JSON.parse(localStorage.getItem('profile')) == null){
            navigate("/auth")
        }
        dispatch(connectws());
    })

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
        <div>
            <Chatlist client={client} currentRoom={currentRoom} setCurrentRoom={setCurrentRoom} clientOpened={clientOpened}/>
            <Grouplist client={client} currentRoom={currentRoom} setCurrentRoom = {setCurrentRoom} clientOpened={clientOpened}/>
            <Chatroom client={client} currentRoom={currentRoom} clientOpened={clientOpened} setClientOpened={setClientOpened}/>
        </div>
    );
}

export default Chat;