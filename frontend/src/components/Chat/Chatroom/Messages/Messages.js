import React from 'react';
import { useSelector } from 'react-redux';

import Message from './Message/Message';

const Messages = () => {
    const messages = useSelector((state) => state.chat);

    return(
        (messages.length === 0) ?  <div/>: <div>
            {messages.map((message) => 
                <Message message = {message} />
            )}
        </div>
    );
}

export default Messages;