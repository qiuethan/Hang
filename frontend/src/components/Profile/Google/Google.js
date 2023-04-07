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
    }

    return (
       <button onClick={connect}>Connect to Google</button>
    )
}

export default Google;