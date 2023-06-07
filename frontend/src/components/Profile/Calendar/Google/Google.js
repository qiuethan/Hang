import React, {useEffect, useState} from 'react';
import {useSearchParams} from "react-router-dom";
import {Button} from "@mui/material";

const Google = () => {

    const [browserSearch, setBrowserSearch] = useSearchParams();
    const [googleCode, setGoogleCode] = useState("");

    useEffect(() => {
        if(browserSearch.get("code") !== null){
            setGoogleCode(browserSearch.get("code"))
        }
        else{
            console.log(browserSearch.get("code"));
        }
    }, [])

    const connect = () => {
        window.location.href = "https://accounts.google.com/o/oauth2/auth?response_type=code&client_id=110686712608-j4udo8p9sckujpgurj9s14ep5jui8tmu.apps.googleusercontent.com&redirect_uri=https%3A%2F%2Fhang-coherentboi.vercel.app%2Fauth&scope=https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fcalendar+https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fuserinfo.email+openid&state=2ZmSqI3ZzCYESHbMgjBV9lbhIX4bwk&prompt=consent&access_type=offline"
    }

    return (
       <Button onClick={connect} sx={{width: "100%", backgroundColor: "#0c7c59", color: "white", ":hover": {color: "#0c7c59", backgroundColor: "white"}}}>Connect to Google to Access Calendar Features!</Button>
    )
}

export default Google;