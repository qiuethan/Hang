import React, { useState, useEffect } from 'react';
import { useDispatch } from 'react-redux';
import { loadmessages } from '../../../actions/chat';

import Form from './Form/Form';
import Messages from './Messages/Messages';

import { Box } from '@mui/material';

const Chatroom = ({ client, currentRoom, clientOpened }) => {

    return(
        <Box sx={{display: "block"}}>
            <Box sx={{display: "flex", flexDirection: "column-reverse"}}>
                <Form client={client} currentRoom={currentRoom}/>
                <Box sx={{display: "flex", flexDirection: "column-reverse", overflow: "auto", height: "calc(98vh - 66px)"}}>
                    <Messages client={client} currentRoom={currentRoom} clientOpened={clientOpened}/>
                </Box>
            </Box>
        </Box>
    );
}

export default Chatroom;