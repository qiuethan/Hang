/*
Author: Ethan Qiu
Filename: Sentlist.js
Last Modified: June 7, 2023
Description: Displays sent friend requests in list
*/

import React, { useEffect, useState } from "react";
import { useSelector } from "react-redux";
import Request from "./Request/Request";
import {Box} from "@mui/material";

const Sentlist = () => {

    //Get requests from react store
    const requests = useSelector((state) => state.sentrequests);

    //Render components in list
    return(
        requests.length === 0 ? <Box/> : <Box sx={{display: "flex", flexDirection:"column", width: "99%", height: "98%", overflowY: "scroll"}}>
            {requests.map((request) => (
                !request.declined && (
                    <Request key={request.to_user} user={request.to_user}/>
                )
            ))}
        </Box>
    )
}

export default Sentlist;