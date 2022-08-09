import React from 'react';
import moment from 'moment';

const Message = ({ message }) => {

    return(
        <div>
            <div>
                {message.user}
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