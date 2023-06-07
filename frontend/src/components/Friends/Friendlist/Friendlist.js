/*
Author: Ethan Qiu
Filename: Friendlist.js
Last Modified: June 7, 2023
Description: Displays friends in list
*/

import React, { useEffect, useState } from "react";
import { useSelector } from "react-redux";
import Friend from "./Friend/Friend";
import {Box} from "@mui/material";

//Friendlist component
const Friendlist = () => {

    //Get friends from react store
    const friends = useSelector(state => state.friends);

    //Render list of friends
    return(
        friends.length === 0 ? <Box/> :
            <Box sx={{display: "flex", flexDirection:"column", width: "99%", height: "98%", overflowY: "scroll"}}>
                {friends.map((friend) => (
                    <Friend key={friend} friend={friend}/>
                ))}
            </Box>
    );
}

export default Friendlist;