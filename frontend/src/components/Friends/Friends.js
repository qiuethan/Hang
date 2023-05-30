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

const Friends = () => {

    const dispatch = useDispatch();

    const [displayRequests, setDisplayRequests] = useState(1);

    const navigate = useNavigate();

    useEffect(() => {
        if(JSON.parse(localStorage.getItem("profile")) === null){
            navigate("/auth");
        }
    }, [localStorage.getItem("profile")]);

    useEffect(() => {
        dispatch(loadfriends());
        dispatch(loadrecievedfriendrequests());
        dispatch(loadsentfriendrequests());
        dispatch(loadblockedusers());
    }, [])

    console.log(useSelector((state) => state.friends));

    const showFriends = () => {
        setDisplayRequests(1);
    }

    const showRequests = () => {
        setDisplayRequests(2);
    }

    const sentRequests = () => {
        setDisplayRequests(3);
    }

    const showBlocked = () => {
        setDisplayRequests(4);
    }

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