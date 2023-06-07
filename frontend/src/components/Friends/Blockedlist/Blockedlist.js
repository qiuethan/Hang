/*
Author: Ethan Qiu
Filename: Blockedlist.js
Last Modified: June 7, 2023
Description: Displays blocked users in list
*/

import React, { useEffect, useState } from "react";
import Blocked from "./Blocked/Blocked";
import {useSelector} from "react-redux";
import {Box} from "@mui/material";

//Blockedlist component
const Blockedlist = () => {

    //Get blocked users from react store
    const blocked = useSelector(state => state.blocked);

    //Render list of blocked users
    return(
        blocked.length === 0 ? <Box/> : <Box sx={{display: "flex", flexDirection:"column", width: "99%", height: "98%", overflowY: "scroll"}}>
        {blocked.map((blocked) => (
                <Blocked key={blocked} blocked={blocked}/>
            ))}
        </Box>
    );
}

export default Blockedlist;