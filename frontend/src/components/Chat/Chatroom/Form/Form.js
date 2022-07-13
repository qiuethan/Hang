import React, { useState } from 'react';

const Form = ({ client }) => {

    const [message, setMessage] = useState("");

    const messageSend = (event) => {
        event.preventDefault();

        client.send(JSON.stringify({
            message: message
        }));

        setMessage("");
    }

    const handleChange = (event) => {
        setMessage(event.target.value);
    }

    return(
        <div>
            <form onSubmit={messageSend}>
                <input 
                    type="text" 
                    name="message" 
                    value={message || ""} 
                    onChange={handleChange} 
                />

                <button type="submit">Send Message</button>
            </form>
        </div>
    );
};

export default Form