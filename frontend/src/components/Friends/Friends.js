/*
Author: Ethan Qiu
Filename: Friends.js
Last Modified: June 7, 2023
Description: Friends page, houses all friends components
*/

import React, {useEffect, useState} from "react";
import { useDispatch, useSelector } from "react-redux";
import {loadblockedusers, loadfriends, loadrecievedfriendrequests, loadsentfriendrequests} from "../../actions/friends";
import Friendlist from "./Friendlist/Friendlist";
import Requestlist from "./Requestlist/Requestlist";
import Request from "./Request/Request";
import Blockedlist from "./Blockedlist/Blockedlist";
import Sentlist from "./Sentlist/Sentlist";
import {Box, Button, Paper} from "@mui/material";
import {useNavigate} from "react-router-dom";

//Friends component
const Friends = () => {

    //Define dispatch
    const dispatch = useDispatch();

    //State variable that toggles between list views
    const [displayRequests, setDisplayRequests] = useState(1);

    //Define navigation variables to route through browser router
    const navigate = useNavigate();

    //On render
    useEffect(() => {
        //If user not logged in, send them to login screen
        if(JSON.parse(localStorage.getItem("profile")) === null){
            navigate("/auth");
        }
    }, [localStorage.getItem("profile")]);

    //On render
    useEffect(() => {
        //Load all friend lists
        dispatch(loadfriends());
        dispatch(loadrecievedfriendrequests());
        dispatch(loadsentfriendrequests());
        dispatch(loadblockedusers());
    }, [])

    //When friend button is clicked
    const showFriends = () => {
        setDisplayRequests(1);
    }

    //When friend request button is clicked
    const showRequests = () => {
        setDisplayRequests(2);
    }

    //When sent request button is clicked
    const sentRequests = () => {
        setDisplayRequests(3);
    }

    //When blocked button is clicked
    const showBlocked = () => {
        setDisplayRequests(4);
    }

    //Render components
    return(
        <Box sx={{display: "flex", width: "100%", height: "100%", justifyContent: "center", alignItems: "center"}}>
            <Paper elevation={16} sx={{width: "98%", height: "96%", borderRadius: "10px"}}>
                <Box sx={{display: "flex", flexDirection: "column", width: "100%", height: "100%"}}>
                    <Box sx={{display: "flex", flexDirection: "row", width: "100%", height: "8%", marginTop: "10px"}}>
                        <Box sx={{display: "flex", width: "50%"}}>
                            <Request/>
                        </Box>
                        <Box sx={{display: "flex", width: "12.5%", marginRight: "10px"}}>
                            <Button onClick={showFriends} disableRipple sx={{width: "100%", height: "100%", "&:hover": {backgroundColor: "#0c7c59", color: "white"}, bgcolor: displayRequests === 1 ? "#0c7c59" : "#a5d6b0", color: displayRequests === 1 ? "white" : "black", borderRadius: "10px"}}>Friends</Button>
                        </Box>
                        <Box sx={{display: "flex", width: "12.5%", marginRight: "10px"}}>
                            <Button onClick={showRequests} disableRipple sx={{width: "100%", height: "100%", "&:hover": {backgroundColor: "#0c7c59", color: "white"}, bgcolor: displayRequests === 2 ? "#0c7c59" : "#a5d6b0", color: displayRequests === 2 ? "white" : "black", borderRadius: "10px"}}>Friend Requests</Button>
                        </Box>
                        <Box sx={{display: "flex", width: "12.5%", marginRight: "10px"}}>
                            <Button onClick={sentRequests} disableRipple sx={{width: "100%", height: "100%", "&:hover": {backgroundColor: "#0c7c59", color: "white"}, bgcolor: displayRequests === 3 ? "#0c7c59" : "#a5d6b0", color: displayRequests === 3 ? "white" : "black", borderRadius: "10px"}}>Sent Friend Requests</Button>
                        </Box>
                        <Box sx={{display: "flex", width: "12.5%", marginRight: "10px"}}>
                            <Button onClick={showBlocked} disableRipple sx={{width: "100%", height: "100%", "&:hover": {backgroundColor: "#0c7c59", color: "white"}, bgcolor: displayRequests === 4 ? "#0c7c59" : "#a5d6b0", color: displayRequests === 4 ? "white" : "black", borderRadius: "10px"}}>Blocked Users</Button>
                        </Box>
                    </Box>
                    <Box sx={{display: "flex", height: "90%", width: "100%", marginTop: "10px", marginLeft: "10px", marginRight: "10px"}}>
                        {
                            displayRequests === 1 && (
                                <Friendlist/>
                            )
                        }
                        {
                            displayRequests === 2 && (
                                <Requestlist/>
                            )
                        }
                        {
                            displayRequests === 3 && (
                                <Sentlist/>
                            )
                        }
                        {
                            displayRequests === 4 && (
                                <Blockedlist/>
                            )
                        }
                    </Box>
                </Box>
            </Paper>
        </Box>

        
    );
}

export default Friends;