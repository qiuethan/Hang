import React, { useState, useEffect, useRef } from 'react';
import { useDispatch } from 'react-redux';
import { loadmessages } from '../../../actions/chat';
import { w3cwebsocket as W3CWebSocket } from "websocket";

import Messages from './Messages/Messages';

const Chatroom = ({ currentRoom }) => {
    const dispatch = useDispatch();
    
    const [client, setClient] = useState();

    useEffect(() => {
        setClient(new W3CWebSocket(`ws://localhost:8000/ws/chat/${currentRoom}/`));
    }, [currentRoom]);

    console.log(client);

    client.onopen = () => {
        console.log("Client Connected");
    }

    client.onmessage = (message) => {
        console.log(message);
    }

    return(
        <Messages/>
        //<Form/>
    );
}

export default Chatroom