/*
Author: Ethan Qiu
Filename: Attendee.js
Last Modified: June 7, 2023
Description: Display attendees of Hang
*/

import React, {useEffect, useState} from "react";
import {Avatar, Box} from "@mui/material";
import {useDispatch, useSelector} from "react-redux";
import {getuser} from "../../../../../actions/users";

//Attendee component
const Attendee = ({attendee}) => {

    //Define dispatch
    const dispatch = useDispatch();

    //Define user state variable
    const [user, setUser] = useState("");

    //Get users from react store
    const users = useSelector(state => state.users);

    //On render
    useEffect(() => {
        //Get user object from react store
        const obj = users.find((user) => user.user.id === attendee)
        //If not found, send to server
        if(obj === undefined){
            dispatch(getuser(attendee));
        }
        else{
            //Set user state to object
            setUser(obj);
        }
    }, [useSelector((state) => state.users)])

    //Render components
    return(
        <Box sx={{display: "block", width: "100%", height: "60px", alignItems: "center", justifyContent: "center", ":hover": {bgcolor: "#a5d6b0"}, borderRadius: "10px", marginBottom: "10px"}}>
            {user !== "" && (
                <Box sx={{display: "flex", width: "100%", height: "90%", alignItems: "center", marginLeft: "10px"}}>
                    <Avatar src={user.profile_picture} sx={{height: "40px", width: "40px"}}/>
                    <h3 style={{margin: "0", fontSize: "20px", marginLeft: "10px"}}>{user !== "" && (user.user.username)}</h3>
                </Box>
            )}
        </Box>
    )
}

export default Attendee;