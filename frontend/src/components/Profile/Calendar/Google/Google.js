/*
Author: Ethan Qiu
Filename: Google.js
Last Modified: June 7, 2023
Description: Allow users to connect calendars via Google Auth
*/

import React, {useEffect, useState} from 'react';
import {useSearchParams} from "react-router-dom";
import {Button} from "@mui/material";

//Google Component
const Google = () => {

    //Define browser search parameters
    const [browserSearch, setBrowserSearch] = useSearchParams();

    //Define google code state variables
    const [googleCode, setGoogleCode] = useState("");

    //On Render
    useEffect(() => {
        //Get code from google
        if(browserSearch.get("code") !== null){
            setGoogleCode(browserSearch.get("code"))
        }
    }, [])

    //Send user to google OAuth screen
    const connect = () => {
        window.location.href = "\n" +
            "https://accounts.google.com/o/oauth2/auth?response_type=code&client_id=110686712608-j4udo8p9sckujpgurj9s14ep5jui8tmu.apps.googleusercontent.com&redirect_uri=https%3A%2F%2Fhang-coherentboi.vercel.app%2Fprofile&scope=https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fcalendar+https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fuserinfo.email+openid&state=2ZmSqI3ZzCYESHbMgjBV9lbhIX4bwk&prompt=consent&access_type=offline"
    }

    //Render component
    return (
       <Button onClick={connect} sx={{width: "100%", backgroundColor: "#0c7c59", color: "white", ":hover": {color: "#0c7c59", backgroundColor: "white"}}}>Connect to Google to Access Calendar Features!</Button>
    )
}

export default Google;