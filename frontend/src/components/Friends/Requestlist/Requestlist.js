/*
Author: Ethan Qiu
Filename: Requestlist.js
Last Modified: June 7, 2023
Description: Displays friend requests in list
*/

import React, { useEffect, useState } from "react";
import { useSelector } from "react-redux";

import Request from "./Request/Request";
import {Box} from "@mui/material";

//Request list component
const Requestlist = () => {

    //Get friend requests from react store
    const requests = useSelector((state) => state.friendrequests);

    //Render
    return(
        requests.length === 0 ? <Box/> : <Box sx={{display: "flex", flexDirection:"column", width: "99%", height: "98%", overflowY: "auto"}}>
        {requests.map((request) => (
                !request.declined && (
                    <Request key={request.from_user} user={request.from_user}/>
                )
            ))}
        </Box>
    )
}

export default Requestlist;