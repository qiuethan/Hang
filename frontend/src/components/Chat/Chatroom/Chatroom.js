import React, { useState, useEffect } from 'react';
import { useDispatch } from 'react-redux';
import { loadmessages } from '../../../actions/chat';

import Form from './Form/Form';
import Messages from './Messages/Messages';

import { Box } from '@mui/material';

const Chatroom = ({ client, currentRoom, clientOpened }) => {

    return(
        <Box sx={{display: "block", height: "98vh"}}>
            <Box sx={{display: "flex", flexDirection: "column-reverse", height: "100%"}}>
                <Form client={client} currentRoom={currentRoom}/>
                <Messages client={client} currentRoom={currentRoom} clientOpened={clientOpened}/>
            </Box>
        </Box>
    );
}

export default Chatroom;