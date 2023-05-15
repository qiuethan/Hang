import React, { useEffect } from "react";
import { useDispatch, useSelector } from "react-redux";
import {loadblockedusers, loadfriends, loadrecievedfriendrequests, loadsentfriendrequests} from "../../actions/friends";
import Friendlist from "./Friendlist/Friendlist";
import Requestlist from "./Requestlist/Requestlist";
import Request from "./Request/Request";
import Blockedlist from "./Blockedlist/Blockedlist";
import Sentlist from "./Sentlist/Sentlist";
import {Box} from "@mui/material";

const Friends = () => {

    const dispatch = useDispatch();

    useEffect(() => {
        dispatch(loadfriends());
        dispatch(loadrecievedfriendrequests());
        dispatch(loadsentfriendrequests());
        dispatch(loadblockedusers());
    }, [])

    console.log(useSelector((state) => state.friends));

    return(
        <Box sx={{display: "flex", width: "100%", height: "100%", justifyContent: "center", alignItems: "center"}}>
            <Box sx={{width: "98%", height: "95%"}}>
                <Request/>
                <h4>Friends:</h4>
                <Friendlist/>
                <h4>Incoming Friend Requests:</h4>
                <Requestlist/>
                <h4>Sent Friend Requests:</h4>
                <Sentlist/>
                <h4>Blocked Users:</h4>
                <Blockedlist/>
            </Box>
        </Box>

        
    );
}

export default Friends;