/*
Author: Ethan Qiu
Filename: Google.js
Last Modified: June 7, 2023
Description: Authentication using google
*/

import React, {useEffect, useState} from 'react';
import {useSearchParams} from "react-router-dom";
import {useDispatch} from "react-redux";
import {googlelogin} from "../../../actions/login";
import {Button} from "@mui/material";

import GoogleIcon from '@mui/icons-material/Google';
import {BASEURL} from "../../../constants/actionTypes";

const Google = () => {

    //initialize dispatch
    const dispatch = useDispatch();

    //intialize search parameters to search address bar
    const [searchParams, setSearchParams] = useSearchParams();

    //On render
    useEffect(() => {
        //search address bar for code parameter
        if(searchParams.get('code') !== null){
            //dispatch action with code then reload
            dispatch(googlelogin(searchParams.get('code').replace("/", "\%2F"), `${BASEURL}auth`)).then((response) => window.location.reload());
        }
        else{
            console.log(searchParams.get('code'));
        }
    }, [])

    //login with google
    const googleAuth = () => {
        //send user to google oAuth
        window.location.href = "https://accounts.google.com/o/oauth2/auth?response_type=code&client_id=110686712608-j4udo8p9sckujpgurj9s14ep5jui8tmu.apps.googleusercontent.com&redirect_uri=https%3A%2F%2Fhang-coherentboi.vercel.app%2Fauth&scope=https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fuserinfo.email+openid&state=2ZmSqI3ZzCYESHbMgjBV9lbhIX4bwk&prompt=consent&access_type=offline";
    }

    //Render Google Login Button
    return (
        <Button disableRipple sx={{bgcolor: "#0c7c59", color: "white", marginBottom: "10px", ":hover": {color: "black"}}} onClick={googleAuth}>
            <GoogleIcon sx={{marginRight: "10px"}}/>Sign in with Google
        </Button>
    )
}

export default Google;