import React, { useEffect, useRef, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { connectws } from '../../../../actions/chat';

import Message from './Message/Message';

import { Box } from '@mui/material';

const Messages = ({ client, currentRoom, clientOpened }) => {
    
    const [messages, setMessages] = useState([]);
    const [sentMessage, setSentMessage] = useState();
    const scrollRef = useRef(null);

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

    useEffect(() => {
        console.log("Scroll Dammit")
        if (scrollRef.current) {
            console.log("Scroll Dammit Scroll")
            scrollRef.current.scrollIntoView({ behaviour: "auto" });
        }
    }, [sentMessage]);

    try{
        client.onmessage = (message) => {
            const messageObject = JSON.parse(message.data);
            if(messageObject.type === "status"){
                if(messageObject.message !== "success"){
                    console.log(message);
                }
            }
            if(messageObject.action === "load_message"){
                setMessages([...messages, ...messageObject.content])
            }
            if(messageObject.action === "send_message"){
                if(messageObject.content.message_channel === currentRoom){
                    setSentMessage(messageObject.content);
                    console.log(messageObject);
                    setMessages([messageObject.content, ...messages])
                }
            }
        }
    }
    catch (error){
        console.log(error);
    }


    function loadMoreMessages() {
        console.log("Hello!")
        console.log(messages);
        client.send(JSON.stringify({
            action: "load_message",
            content: {
                message_channel: currentRoom,
                message_id: messages[messages.length - 1].id - 1
            }
        }));
    }

    const handleScroll = (event) => {

        const { scrollTop, clientHeight, scrollHeight } = event.target;

        if (Math.ceil(scrollTop * (-1) + clientHeight) >= scrollHeight) {
            loadMoreMessages();
        }
    };

    return(
        messages.length === 0 ? <Box/> :
            <Box sx={{display: "block", height: "100%", width: "100%"}}>
                <Box sx={{display: "flex", height: "calc(98vh - 130px)", flexDirection: "column-reverse", overflowY: "scroll"}} onScroll={handleScroll}>
                    {messages.map((message) => (
                        <Message key={message.id} message={message}/>
                    ))}
                </Box>
            </Box>
    );
}

export default Messages;