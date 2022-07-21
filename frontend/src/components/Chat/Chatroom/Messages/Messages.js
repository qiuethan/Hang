import React, { useEffect, useState } from 'react';
import { useSelector } from 'react-redux';

import Message from './Message/Message';

const Messages = ({ client, currentRoom, clientOpened }) => {
    
    const [messages, setMessages] = useState([]);

    useEffect(() => {
        if(clientOpened && currentRoom !== undefined){
            client.send(JSON.stringify({
                type: "load_message",
                message_channel: {
                    id: currentRoom
                }
            }));
        }
        console.log(currentRoom);
    }, [currentRoom, clientOpened]);

    client.onmessage = (message) => {
        console.log(message);
        const messageObject = JSON.parse(message.data);
        if(messageObject.type === "status"){
            if(messageObject.message !== "success"){
                console.log(message);
            }
        }
        if(messageObject.type === "load_message"){
            setMessages([...messages, ...messageObject.messages])
        }
        if(messageObject.type === "receive_message"){
            if(messageObject.message.message_channel.id === currentRoom){  
                setMessages([messageObject.message, ...messages])
            }
            else{
                
            }
        }
    }

    console.log(messages);

    return(
        messages.length === 0 ? <div/> : <div>
            {messages.map((message) => (
                <Message message={message}/>
            ))}
        </div>
    );
}

export default Messages;