import React, { useEffect, useState, useRef } from 'react';
import { w3cwebsocket as W3CWebSocket } from "websocket";

import Chatroom from './Chatroom/Chatroom';
import Chatlist from './Chatlist/Chatlist';

const Chat = () => {

    const [currentRoom, setCurrentRoom] = useState();
    const [client] = useState(new W3CWebSocket(`ws://localhost:8000/ws/chat/${JSON.parse(localStorage.getItem('profile')).user.username}/`));
    
    const [clientOpened, setClientOpened] = useState(false);

    client.onopen = () => {
        console.log("Client Connected");
        client.send(JSON.stringify({
            token: JSON.parse(localStorage.getItem('profile')).token
        }));
        setClientOpened(true);
    }

    client.onclose = () => {
        setClientOpened(false);
    }

    return(
        <div>
            <Chatlist client={client} currentRoom={currentRoom} setCurrentRoom={setCurrentRoom} clientOpened={clientOpened}/>
            <Chatroom client={client} currentRoom={currentRoom} clientOpened={clientOpened} setClientOpened={setClientOpened}/>
        </div>
    );
}

export default Chat;