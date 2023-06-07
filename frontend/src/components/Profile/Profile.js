/*
Author: Ethan Qiu
Filename: Profile.js
Last Modified: June 7, 2023
Description: Display profile page for user
*/

import React, {useEffect} from "react";
import {useSelector, useDispatch} from "react-redux";
import {useNavigate} from "react-router-dom";
import {getself} from "../../actions/users";
import User from "./User/User";
import {Box, Paper} from "@mui/material";
import Calendar from "./Calendar/Calendar";

//Profile Component
const Profile = ({currentPage, setCurrentPage}) => {

    //Get user from react store
    const user = useSelector(state => state.profile);

    //Define dispatch variable
    const dispatch = useDispatch();

    //Define navigation variable
    const navigate = useNavigate();

    //On render
    useEffect(() => {
        //If not logged in, send to auth
        if(JSON.parse(localStorage.getItem("profile")) === null){
            navigate("/auth");
        }
    }, [localStorage.getItem("profile")]);

    //On render
    useEffect(() => {
        //Get self user object
        dispatch(getself());
    }, [])

    //Render components
    return(
        <Box sx={{display: "flex", width: "100%", height: "100%", justifyContent: "center", alignItems: "center"}}>
            <Paper elevation={16} sx={{display:"flex", width: "98%", height: "96%", alignItems: "center", justifyContent: "center", borderRadius: "10px"}}>
                <Box sx={{display: "flex", width: "98%", height: "90%", flexDirection: "column", alignItems: 'center'}}>
                    <Box sx={{display: "flex", justifyContent: "center", width: "100%", height: "40%", marginBottom: "20px"}}>
                        <User/>
                    </Box>
                    <Box sx={{display: "flex", width: "90%", justifyContent: "center", height: "60%"}}>
                        <Calendar/>
                    </Box>
                </Box>
            </Paper>
        </Box>
    )
}

export default Profile;