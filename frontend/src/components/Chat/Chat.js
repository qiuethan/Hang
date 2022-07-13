import React, { useEffect, useState, useRef } from 'react';
import { w3cwebsocket as W3CWebSocket } from "websocket";

import Chatroom from './Chatroom/Chatroom';
import Chatlist from './Chatlist/Chatlist';

const Chat = () => {

    const [currentRoom, setCurrentRoom] = useState("PWBnraqmcp");
    const [client, setClient] = useState(new W3CWebSocket(`ws://localhost:8000/ws/chat/${JSON.parse(localStorage.getItem('profile')).user.username}/`));

    return(
        <div>
            <Chatlist client={client} currentRoom={currentRoom} setCurrentRoom={setCurrentRoom}/>
            <Chatroom client={client} currentRoom={currentRoom}/>
        </div>
    );
}

export default Chat;