import React, { useEffect, useState } from 'react';
import { useSelector } from 'react-redux';

import Message from './Message/Message';

const Messages = ({ client, currentRoom, clientOpened }) => {
    
    const [messages, setMessages] = useState([]);

    useEffect(() => {
        setMessages([]);
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

    try{
        client.onmessage = (message) => {
            const messageObject = JSON.parse(message.data);
            console.log(messageObject);
            if(messageObject.action === "status"){
                if(messageObject.message !== "success"){
                    console.log(message);
                }
            }
            if(messageObject.action === "load_message"){
                setMessages([...messages, ...messageObject.content.messages])
            }
            if(messageObject.action === "send_message"){
                if(messageObject.content.message.message_channel.id === currentRoom){  
                    setMessages([messageObject.content.message, ...messages])
                }
                else{
                    
                }
            }
        }
    }
    catch (error){
        console.log(error);
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