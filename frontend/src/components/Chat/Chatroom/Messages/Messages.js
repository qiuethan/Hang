/*
Author: Ethan Qiu
Filename: Messages.js
Last Modified: June 7, 2023
Description: Display messages in chatroom
*/

import React, { useEffect, useRef, useState } from 'react';
import { useDispatch } from 'react-redux';
import {loadgroups, loadrooms} from '../../../../actions/chat';
import Message from './Message/Message';
import { Box } from '@mui/material';

// Messages Component
const Messages = ({ client, currentRoom, clientOpened }) => {

    const [messages, setMessages] = useState([]);  // Keeps track of all messages in current room
    const [sentMessage, setSentMessage] = useState();  // State to keep track of sent message
    const scrollRef = useRef(null);  // Ref for scrolling functionality
    const dispatch = useDispatch();  // Dispatch for redux

    // useEffect to load messages whenever there's a change in currentRoom or clientOpened
    useEffect(() => {
        setMessages([]);
        if(currentRoom !== undefined){
            client.send(JSON.stringify({
                action: "load_message",
                content: {
                    message_channel: currentRoom
                }
            }));
        }
        if (scrollRef.current) {
            scrollRef.current.scrollIntoView({ behaviour: "auto" });
        }
    }, [currentRoom, clientOpened]);

    // useEffect to manage scrolling when a new message is sent
    useEffect(() => {
        if (scrollRef.current) {
            console.log("Scroll Dammit Scroll")
            scrollRef.current.scrollIntoView({ behaviour: "auto" });
        }
    }, [sentMessage]);

    // Handle new messages received from the websocket
    try{
        client.onmessage = (message) => {
            dispatch(loadrooms());
            dispatch(loadgroups());
            const messageObject = JSON.parse(message.data);
            if(messageObject.type === "status"){
                if(messageObject.message !== "success"){
                    console.log(message);
                }
            }
            if(messageObject.action === "load_message"){
                setMessages([...messages, ...messageObject.content])  // Add new messages to the state
            }
            if(messageObject.action === "send_message"){
                if(messageObject.content.message_channel === currentRoom){
                    setSentMessage(messageObject.content);
                    setMessages([messageObject.content, ...messages])  // Add sent message to the state
                }
            }
        }
    }
    catch (error){
        console.log(error);  // Log errors
    }

    // Function to load more messages
    function loadMoreMessages() {
        client.send(JSON.stringify({
            action: "load_message",
            content: {
                message_channel: currentRoom,
                message_id: messages[messages.length - 1].id - 1
            }
        }));
    }

    // Function to handle scroll events
    const handleScroll = (event) => {

        const { scrollTop, clientHeight, scrollHeight } = event.target;

        if (Math.ceil(scrollTop * (-1) + clientHeight) >= scrollHeight) {
            loadMoreMessages();  // Load more messages when scroll reaches top
        }
    };

    // Render
    return(
        messages.length === 0 ? <Box/> :
            <Box sx={{display: "block", height: "100%", width: "100%"}}>
                <Box sx={{display: "flex", height: "calc(98vh - 135px)", flexDirection: "column-reverse", overflowY: "scroll"}} onScroll={handleScroll}>
                    {messages.map((message) => (
                        <Message key={message.id} message={message}/>
                    ))}
                </Box>
            </Box>
    );
}

export default Messages;