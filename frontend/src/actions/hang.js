/*
Author: Ethan Qiu
Filename: hang.js
Last Modified: June 7, 2023
Description: Action methods pertaining to Hang API calls
*/

import * as api from '../api/index.js';

import { CREATEHANGEVENT, GETHANGEVENTS } from '../constants/actionTypes.js'

//action to create hang event using Hang Event API
export const createhangevent = (inputs) => async(dispatch) => {
    try{
        //store return as variable
        const { data } = await api.createhangevent({...inputs, scheduled_time_start: inputs.scheduled_time_start + new Date().toString().match(/([-\+][0-9]+)\s/)[1], scheduled_time_end: inputs.scheduled_time_end + new Date().toString().match(/([-\+][0-9]+)\s/)[1]});

        //update react store via reducers
        dispatch({type: CREATEHANGEVENT, payload: data})

        //return data to component
        return data;
    }
    catch (error){
        console.log(error);
    }
}

//action to get hang events from Hang Event API
export const gethangevents = () => async(dispatch) => {
    try{

        //store return as variable
        const { data } = await api.gethangevents();

        //update react store via reducers
        dispatch({type: GETHANGEVENTS, payload: data})
    }
    catch(error){
        console.log(error);
    }
}

//action to join hang event from Hang Event API
export const joinhangevent = (code, navigate) => async(dispatch) => {
    try{
        //store return as variable
        const { data } = await api.joinhangevent(code);

        //return data to component
        return data;
    }
    catch(error){
        console.log(error);
    }
}

//action to generate join link using Hang Event API
export const generatejoinlink = (id) => async(dispatch) => {
    try{
        //store return as variable
        const { data } = await api.generatecode(id);

        //return data to component
        return data;
    }
    catch (error){
        console.log(error);
    }
}

//action to add hang event to calendar using Hang Event API
export const addtocalendar = (id) => async(dispatch) => {
    try{
        //store return as variable
        const { data } = await api.addtocalendar(id);

        //return data to component
        return data;
    }
    catch (error){
        console.log(error);
    }
}