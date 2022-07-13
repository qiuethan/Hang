import React, { useState, useEffect } from 'react';
import { useDispatch } from 'react-redux';
import { loadmessages } from '../../../actions/chat';

import Form from './Form/Form';
import Messages from './Messages/Messages';

const Chatroom = ({ client, currentRoom }) => {

    const [clientOpened, setClientOpen] = useState(false);

    client.onopen = () => {
        console.log("Client Connected");
        setClientOpen(true);
    }

    client.onmessage = (message) => {
        console.log(message);
    }

    return(
        <div>
            <Messages client={client} currentRoom={currentRoom} clientOpened={clientOpened}/>
            <Form client={client}/>
        </div>
    );
}

export default Chatroom