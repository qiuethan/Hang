import React, {useEffect, useState} from 'react';
import {useSearchParams} from "react-router-dom";
import {useDispatch} from "react-redux";
import {googlelogin} from "../../../actions/login";
import {Button} from "@mui/material";

import GoogleIcon from '@mui/icons-material/Google';

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
        window.location.href = "https://accounts.google.com/o/oauth2/auth?response_type=code&client_id=110686712608-j4udo8p9sckujpgurj9s14ep5jui8tmu.apps.googleusercontent.com&redirect_uri=https%3A%2F%2Fhang-coherentboi.vercel.app%2Fauth&scope=https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fuserinfo.email+openid&state=2ZmSqI3ZzCYESHbMgjBV9lbhIX4bwk&prompt=consent&access_type=offline";
    }

    return (
        <Button disableRipple sx={{bgcolor: "#0c7c59", color: "white", marginBottom: "10px", ":hover": {color: "black"}}} onClick={googleAuth}>
            <GoogleIcon sx={{marginRight: "10px"}}/>Sign in with Google
        </Button>
    )
}

export default Google;