import React, { useEffect, useState, useRef } from 'react';
import { w3cwebsocket as W3CWebSocket } from "websocket";

import Chatroom from './Chatroom/Chatroom';
import Chatlist from './Chatlist/Chatlist';
import { useDispatch, useSelector } from 'react-redux';
import { connectws } from '../../actions/chat';

const Chat = () => {

    const [currentRoom, setCurrentRoom] = useState();
    const client = useSelector(state => state.websocket);

    const [clientOpened, setClientOpened] = useState(false);

    const dispatch = useDispatch();

    console.log(useSelector(state => state.websocket))

    useEffect(() => {
        dispatch(connectws());
    })

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