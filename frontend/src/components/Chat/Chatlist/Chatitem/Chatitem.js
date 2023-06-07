/*
Author: Ethan Qiu
Filename: Chatitem.js
Last Modified: June 7, 2023
Description: Displays information for chatlist and grouplist
*/

import React, { useEffect, useState } from "react";
import { useDispatch, useSelector} from "react-redux";
import {getuser} from "../../../../actions/users";
import {Avatar, Box, Button} from "@mui/material";

// Chatitem component
const Chatitem = ({ roomid, users, type, gcName, currentRoom, setCurrentRoom }) => {

    // Define dispatch
    const dispatch = useDispatch();

    // On Click
    const handleClick = (event) => {
        event.preventDefault();
        // Set Room Id To Room Id
        setCurrentRoom(roomid);
    }

    // Get users from react store
    const userStorage = useSelector(state => state.users);

    // Define state variables for name + picture
    const [name, setName] = useState("");
    const [picture, setPicture] = useState("");

    // On render
    useEffect(() => {
        if(type === "DM"){
            try{
                // Find other user's id
                const otherUserId = JSON.parse(users).find(user => user !== JSON.parse(localStorage.getItem("profile")).user.id);
                // Get other user's object using id
                const obj = userStorage.find((user) => user.user.id === otherUserId);
                // If not found
                if(obj === undefined){
                    // Send search request to server
                    dispatch(getuser(otherUserId));
                }
                else{
                    // Set name + picture to that of other user
                    setName(obj.user.username);
                    setPicture(obj.profile_picture);
                }
            }
            catch (error){
                setName("Could Not Access User");
            }
        }
        if(type === "GC"){
            // Set name to gcName
            setName(gcName);
        }
    }, [useSelector(state => state.users)]);

    //Render
    return(
        <Box sx={{width: "100%", height: "60px"}}>
            <Button
                disableRipple
                onClick={handleClick}
                sx={{width: "100%", height: "100%", "&:hover": {backgroundColor: "#a5d6b0"}, borderRadius: "0", backgroundColor: roomid === currentRoom ? "#0c7c59" : ""}}
            >
                <Box sx={{display: "flex", flexDirection: "row", width: "100%"}}>
                    <Box sx={{width: "20%", height: "100%"}}>
                        <Avatar src={picture} sx={{aspectRatio: "1"}}/>
                    </Box>
                    <h3 style={{margin: "0", alignSelf:"center", marginLeft: "10px", color: roomid === currentRoom ? "white" : "black", overflowX: "scroll"}}>{name}</h3>
                </Box>
            </Button>
        </Box>

    );
};

export default Chatitem;