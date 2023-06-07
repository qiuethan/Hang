/*
Author: Ethan Qiu
Filename: User.js
Last Modified: June 7, 2023
Description: Display users of hang on mini view
*/

import React, {useEffect, useState} from "react";
import {Box} from "@mui/material";
import {useDispatch, useSelector} from "react-redux";
import {getuser} from "../../../../actions/users";

//User component
const User = ({attendee}) => {

    //Define dispatch variable
    const dispatch = useDispatch();

    //Define friend state variable
    const [friend, setFriend] = useState("");

    //Get users from react store
    const users = useSelector(state => state.users);

    //On render
    useEffect(() => {
        //Find user object via user id
        const obj = users.find((user) => user.user.id === attendee)
        //If not found
        if(obj === undefined){
            //Send to API
            dispatch(getuser(attendee));
        }
        else{
            //Set friend as user object
            setFriend(obj.user.username);
        }
    }, [useSelector((state) => state.users)])

    //Render components
    return(
        <Box>
            {friend !== "" && (
                friend
            )}
        </Box>
    )
}

export default User;