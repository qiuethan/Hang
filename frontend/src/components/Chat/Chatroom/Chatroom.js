import React, { useState, useEffect } from 'react';
import { useDispatch } from 'react-redux';

import Messages from './Messages/Messages';

const Chatroom = ({ currentRoom }) => {
    const dispatch = useDispatch();

    useEffect(() => {
        dispatch(getChat(currentRoom))
    }, [currentRoom, dispatch]);

    return(
        <Messages/>
        //<Form/>
    );
}

export default Chatroom