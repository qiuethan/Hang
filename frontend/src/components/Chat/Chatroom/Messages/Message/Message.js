import React from 'react';
import moment from 'moment';

const Message = ({ message }) => {

    return(
        //Message
        <div>
            <div>
                {message.message}
            </div>
            <div>
                {new Date(message.created_at*1000).toLocaleDateString()}
            </div>
        </div>
    )
}

export default Message