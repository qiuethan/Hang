import React from 'react';
import { useSelector } from 'react-redux';

import Message from './Message/Message';

const Messages = () => {

    useSelector((state) => console.log(state));
    const messages = useSelector((state) => state.chat);
    
    console.log(messages)

    return(
        (messages.length === 0) ?  <div/>: <div>
            {messages.map((message) => 
                <Message message = {message} />
            )}
        </div>
    );
}

export default Messages;