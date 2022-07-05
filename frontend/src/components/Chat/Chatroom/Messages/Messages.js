import React from 'react';
import { useSelector } from 'react-redux';

import Message from './Message/Message';

const Messages = () => {
    const messages = useSelector((state) => state.messages);
    
    return(
        !messages.length ?  <div/>: <div>
            {messages.map((message) => 
                <Message message = {message} />
            )}
        </div>
    );
}

export default Messages;