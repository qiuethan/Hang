/*
Author: Ethan Qiu
Filename: Verify.js
Last Modified: June 7, 2023
Description: Allows user to verify email using link
*/

import React, { useEffect } from "react";
import {useNavigate, useSearchParams} from "react-router-dom";

import axios from "axios";
import {BASEURL} from "../../constants/actionTypes";

//Verify Component
const Verify = () => {

    //Define search parameters
    const [searchParams, setSearchParams] = useSearchParams();

    //Define navigation variable
    const navigate = useNavigate();

    //Set API baseURL
    const API = axios.create({ baseURL: BASEURL})

    //Get verification key from search bar
    const getKey = () => {
        return searchParams.get("key");
    }

    //Validate verification key
    const validate = async (key) => {
        try{
            //Call backend in attempt to verify
            await API.delete(`/v1/accounts/email_verification_tokens/${key}/`);
        }
        catch(error){
            console.log(error);
        }
    }

    //When user presses return to home
    const returnToAuth = () => {
        navigate("/auth");
    }

    //On render
    useEffect(() => {
        //Get key from search bar
        const key = getKey();
        //Validate key
        validate(key).then((response) => console.log(response));
    }, []);

    //Render components
    return(
        <div>
            <div>Verified</div>
            <button onClick={returnToAuth}>Click here to return to login page</button>
        </div>
    );
};

export default Verify;