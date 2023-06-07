/*
Author: Ethan Qiu
Filename: users.js
Last Modified: June 7, 2023
Description: Action methods pertaining to user API calls
*/

import * as api from '../api/index.js';

import {GETSELF, GETUSER} from '../constants/actionTypes.js'

//action to get user's information via user API call
export const getself = () => async(dispatch) => {
    try{
        //save return values to variable
        const { data } = await api.getcurrentuser();

        //update react store via reducers
        dispatch({type: GETSELF, payload: data})
    }
    catch(error){
        console.log(error);
    }
}

//action to get user with id via user API call
export const getuser = (id) => async(dispatch) => {
    try{
        //save return values to variable
        const { data } = await api.getuser(id);

        //update react store via reducers
        dispatch({ type: GETUSER, payload: data })

        return data;
    }
    catch(error){
        console.log(error)
    }
};

//action to get user by username via user API calls
export const getuserbyusername = (username) => async(dispatch) => {
    try{
        //save return values to variable
        const { data } = await api.getuserbyusername(username);

        //update react store via reducers
        dispatch({ type: GETUSER, payload: data })

        //return data back to component
        return data;
    }
    catch(error){
        console.log(error);
    }
}

//action to get user by email using user API calls
export const getuserbyemail = (email) => async(dispatch) => {
    try{
        //store return values in variable
        const { data } = await api.getuserbyemail(email);

        //update react store via reducers
        dispatch({ type: GETUSER, payload: data })

        //return data to components
        return data;
    }
    catch(error){
        console.log(error);
    }
}

//action to update profile using user API calls
export const updateProfile = (picture, aboutMe) => async(dispatch) => {
    try{
        //update profile pictures and about me
        await api.updatepicture(picture);
        await api.updateaboutme(aboutMe);

        //call getself to update values to react store
        await getself();
    }
    catch (error){
        console.log(error);
    }
}