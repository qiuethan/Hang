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
        window.location.href = "https://accounts.google.com/o/oauth2/auth?response_type=code&client_id=110686712608-j4udo8p9sckujpgurj9s14ep5jui8tmu.apps.googleusercontent.com&redirect_uri=http%3A%2F%2Flocalhost%3A3000%2Fprofile&scope=https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fcalendar+https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fuserinfo.email+openid&state=ALAB1NoseJPLZL5qSIwGofluq0oU7m&prompt=consent&access_type=offline"
    }

    return (
        <button onClick={googleAuth}>Sign in with Google</button>
    )
}

export default Google;