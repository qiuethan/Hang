import React from 'react';
import moment from 'moment';

const Message = ({ message }) => {

    return(
        //Message
        <div>
            <div>
                {message.user.username}
            </div>
            <div>
                {message.content}
            </div>
            <div>
                {new Date(message.created_at).toLocaleDateString()}
            </div>
        </div>
    )
}

export default Message