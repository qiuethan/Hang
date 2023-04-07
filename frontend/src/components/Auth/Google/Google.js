import React, {useEffect, useState} from 'react';
import {useSearchParams} from "react-router-dom";
import {useDispatch} from "react-redux";
import {googlelogin} from "../../../actions/login";

const Google = () => {

    const dispatch = useDispatch();

    const [searchParams, setSearchParams] = useSearchParams();

    useEffect(() => {
        if(searchParams.get('code') !== null){
            dispatch(googlelogin(searchParams.get('code').replace("/", "\%2F"))).then((response) => window.location.reload());
        }
        else{
            console.log(searchParams.get('code'));
        }
    }, [])

    const googleAuth = () => {
        window.location.href = "https://accounts.google.com/o/oauth2/auth?client_id=110686712608-j4udo8p9sckujpgurj9s14ep5jui8tmu.apps.googleusercontent.com&redirect_uri=http://localhost:3000/auth&scope=email&response_type=code&include_granted_scopes=true&access_type=offline&state=state_parameter_passthrough_value"
    }

    return (
        <button onClick={googleAuth}>Sign in with Google</button>
    )
}

export default Google;