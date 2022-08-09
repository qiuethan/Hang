import React, { useEffect, useState } from 'react';
import { useSelector } from 'react-redux';

import Message from './Message/Message';

const Messages = ({ client, currentRoom, clientOpened }) => {
    
    const [messages, setMessages] = useState([]);

    useEffect(() => {
        setMessages([]);
        if(clientOpened && currentRoom !== undefined){
            client.send(JSON.stringify({
                action: "load_message",
                content: {
                    message_channel_id: currentRoom
                }
            }));
        }
    }, [currentRoom, clientOpened]);

    try{
        client.onmessage = (message) => {
            const messageObject = JSON.parse(message.data);
            if(messageObject.action === "status"){
                if(messageObject.message !== "success"){
                    console.log(message);
                }
            }
            if(messageObject.action === "load_message"){
                setMessages([...messages, ...messageObject.content])
            }
            if(messageObject.action === "send_message"){
                if(messageObject.content.message_channel.id === currentRoom){  
                    setMessages([messageObject.content, ...messages])
                }
                else{
                    
                }
            }
        }
    }
    catch (error){
        console.log(error);
    }    

    return(
        messages.length === 0 ? <div/> : <div>
            {messages.map((message) => (
                <Message key={message.id} message={message}/>
            ))}
        </div>
    );
}

export default Messages;