import React, {useEffect, useState} from 'react';
import {useSearchParams} from "react-router-dom";

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
        window.location.href = "https://accounts.google.com/o/oauth2/auth?client_id=110686712608-j4udo8p9sckujpgurj9s14ep5jui8tmu.apps.googleusercontent.com&redirect_uri=http://localhost:3000/profile&scope=https://www.googleapis.com/auth/calendar+https://www.googleapis.com/auth/userinfo.email&response_type=code&include_granted_scopes=true&access_type=offline&state=state_parameter_passthrough_value"
    }

    return (
       <button onClick={connect}>Connect to Google</button>
    )
}

export default Google;