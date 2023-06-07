/*
Author: Ethan Qiu
Filename: calendar.js
Last Modified: June 7, 2023
Description: Action methods pertaining to Calendar API calls
*/

import * as api from "../api/index";

//action to get values of google calendar from api
export const getgooglecalendar = () => async(dispatch) => {
    try{
        //async call + stores data
        const { data } = await api.getgooglecalendar();
        //returns data back to component
        return data;
    }
    catch(error){
        //error will notify component
        return error.response.data[0];
    }
}

//action to sync user's google calendars with hang application
export const syncgooglecalendar = (syncedcalendar) => async(dispatch) => {
    try{
        //retrieves data from api and posts synced calendars to backend
        const { data } = await api.syncgooglecalendar(syncedcalendar);
        //returns data to component
        return data;
    }
    catch(error){
        //catch error
        console.log(error);
    }
}