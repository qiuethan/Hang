/*
Author: Ethan Qiu
Filename: Chatroom.js
Last Modified: June 7, 2023
Description: Chatroom portion of chat feature
*/

import React, { useState, useEffect } from 'react';

import Form from './Form/Form';
import Messages from './Messages/Messages';
import Settings from './Settings/Settings';
import {Box, Paper} from '@mui/material';

const Chatroom = ({ client, currentRoom, clientOpened }) => {

    // Create State for Settings
    const [settings, setSettings] = useState(false);

    // On Render
    useEffect(() => {
        setSettings(false);
    }, [currentRoom])

    // Render UI
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