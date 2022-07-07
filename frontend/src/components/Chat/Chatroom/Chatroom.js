import React, { useState, useEffect } from 'react';
import { useDispatch } from 'react-redux';
import { loadmessages } from '../../../actions/chat';

import Messages from './Messages/Messages';

const Chatroom = ({ currentRoom }) => {
    const dispatch = useDispatch();
    
    dispatch(loadmessages(currentRoom, 1657217156));

    useEffect(() => {
        dispatch(loadmessages(currentRoom, 1657217156))
    }, [currentRoom, dispatch]);

    return(
        <Messages/>
        //<Form/>
    );
}

export default Chatroom