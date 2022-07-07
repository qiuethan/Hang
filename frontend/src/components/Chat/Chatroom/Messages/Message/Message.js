import React from 'react';
import { useDispatch } from 'react-redux';
import moment from 'moment';

const Message = ({ message }) => {
    const dispatch = useDispatch();
    const user = JSON.parse(localStorage.getItem('profile'));

    console.log(message.time);

    return(
        //Message
        <div>
            <div>
                {message.message}
            </div>
            <div>
                {new Date(message.time*1000).toLocaleDateString()}
            </div>
        </div>
    )
}

export default Message