import React, { useState } from 'react';

const Form = ({ client, currentRoom }) => {

    const [message, setMessage] = useState("");

    const messageSend = (event) => {
        event.preventDefault();

        client.send(JSON.stringify({
            action: "send_message",
            content: {
                message_channel: {
                    id: currentRoom
                },
                content: message
            }
        }));

        setMessage("");
    }

    const handleChange = (event) => {
        setMessage(event.target.value);
    }

    return(
        <div>
            {
                JSON.parse(localStorage.getItem('profile') !== null) &&
                <form onSubmit={messageSend}>
                    <input 
                        type="text" 
                        name="message" 
                        value={message || ""} 
                        onChange={handleChange} 
                    />

                    <button type="submit">Send Message</button>
                </form>
            }
            
        </div>
    );
};

export default Form