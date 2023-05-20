import React, { useEffect, useState } from "react";
import { useSelector } from "react-redux";

import Request from "./Request/Request";
import {Box} from "@mui/material";

const Requestlist = () => {

    const requests = useSelector((state) => state.friendrequests);

    console.log(requests);

    return(
        requests.length === 0 ? <Box/> : <Box sx={{display: "flex", flexDirection:"column", width: "99%", height: "98%", overflowY: "scroll"}}>
        {requests.map((request) => (
                !request.declined && (
                    <Request key={request.from_user} user={request.from_user}/>
                )
            ))}
        </Box>
    )
}

export default Requestlist;