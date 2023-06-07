/*
Author: Ethan Qiu
Filename: login.js
Last Modified: June 7, 2023
Description: Action methods pertaining to Login API calls
*/

import * as api from '../api/index.js'
import { LOGIN, LOGOUT } from '../constants/actionTypes'

//action to login user using Login API
export const login = (inputs) => async (dispatch) => {
    try{
        //store return as variable
        const { data } = await api.login(inputs);

        //update react store via reducers
        dispatch({ type: LOGIN, data });
    }
    catch(error){
        console.log(error);
        return(error);
    }
}

//action to sign up using Login API
export const signup = (inputs, navigate) => async (dispatch) => {
    try{
        //return value here is actually null, so don't need const {data}
        const { data } = await api.signin(inputs);

        //redirect page to /auth
        navigate("/auth")
    }
    catch (error){
        console.log(error);
    }
}

//action to send email to user email using Login API
export const sendemail = (inputs) => async (dispatch) => {
    try{
        //no return value on data once again, so don't need const {data}
        const { data } = await api.sendemail(inputs);
    }
    catch(error){
        console.log(error);
    }
}

//Action to log out user using Friends API
export const logout = (token) => async(dispatch) => {
    try{
        //no return value
        const res = await api.logout(token);

        //update react store via reducer
        dispatch({type: LOGOUT});

    }
    catch (error){
        console.log(error);
    }
}

//Action to login using google using Login API
export const googlelogin = (code) => async(dispatch) => {
    try{
        //store return as variable
        const { data } = await api.googlelogin(code);

        //update react store via reducers
        dispatch({type: LOGIN, data})
    }
    catch(error){
        console.log(error);
    }
}