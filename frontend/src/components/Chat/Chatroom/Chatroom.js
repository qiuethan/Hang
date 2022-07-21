import React, { useState, useEffect } from 'react';
import { useDispatch } from 'react-redux';
import { loadmessages } from '../../../actions/chat';

import Form from './Form/Form';
import Messages from './Messages/Messages';

const Chatroom = ({ client, currentRoom, clientOpened }) => {

    return(
        <div>
            <Messages client={client} currentRoom={currentRoom} clientOpened={clientOpened}/>
            <Form client={client} currentRoom={currentRoom}/>
        </div>
    );
}

export default Chatroom