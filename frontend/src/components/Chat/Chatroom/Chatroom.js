import React, { useState, useEffect } from 'react';
import {useDispatch, useSelector} from 'react-redux';
import { loadmessages } from '../../../actions/chat';

import Form from './Form/Form';
import Messages from './Messages/Messages';
import Settings from './Settings/Settings';

import {Box, Paper} from '@mui/material';

const Chatroom = ({ client, currentRoom, clientOpened }) => {

    const [settings, setSettings] = useState(false);

    useEffect(() => {
        setSettings(false);
    }, [currentRoom])

    return(
        <Paper elevation={16} sx={{display: "flex", height: "100%", width: "100%", borderRadius: "10px"}}>

                <Box sx={{display: "flex", flexDirection:"column", height: "100%", width: "100%"}}>
                    {currentRoom && (
                        <Box sx={{height: "9%"}}>
                            <Settings currentRoom={currentRoom} settings={settings} setSettings={setSettings}/>
                        </Box>
                    )}
                    {!settings && currentRoom && (
                        <Box sx={{height: "82%", width: "100%", display: "flex", flexDirection:"column"}}>
                            <Messages client={client} currentRoom={currentRoom} clientOpened={clientOpened}/>
                        </Box>
                    )}
                    {!settings && currentRoom && (
                        <Box sx={{height: "9%", bgcolor:"#0c7c59", borderRadius: "0 0 10px 10px"}}>
                            <Form client={client} currentRoom={currentRoom}/>
                        </Box>
                    )}
                </Box>
        </Paper>
    );
}

export default Chatroom;