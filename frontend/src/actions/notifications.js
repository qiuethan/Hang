/*
Author: Ethan Qiu
Filename: notifications.js
Last Modified: June 7, 2023
Description: Action methods pertaining to Notification API calls
*/

import { w3cwebsocket as W3CWebSocket } from "websocket";
import * as api from "../api/index.js";
import {BASEWS, CONNECTRTWS, GETUNREADNOTIFICATIONS} from "../constants/actionTypes";

//Action to get unread notifications via Notifications API
export const getUnreadNotifications = () => async(dispatch) => {
    try{

        //store return as variable
        const {data} = await api.getunreadnotifications();

        //update react store via reducers
        dispatch({type: GETUNREADNOTIFICATIONS, payload: data});
    }
    catch(error){
        console.log(error);
    }
}

//define websocket endpoint to connect websocket to backend
const connect = new Promise(function(success, failure) {
    try{
        //define connection endpoint
        let connection = JSON.parse(localStorage.getItem('profile')) !== null ? new W3CWebSocket(`${BASEWS}ws/real_time_ws/${JSON.parse(localStorage.getItem('profile')).user.username}/`) : null;
        //on success, return success
        connection.onopen = () => success(connection);
        //on error, return failure
        connection.onerror = () => failure();
    }
    catch(error){
        failure();
    }
});

//connect websocket to backend
export const connectRTWS = () => (dispatch) => {
    try {
        //after connecting...
        connect.then(
            function (connection) {
                try {
                    //authenticate user in websocket
                    connection.send(JSON.stringify({
                        action: "authenticate",
                        content: {
                            token: JSON.parse(localStorage.getItem('profile')).token
                        }
                    }));
                } catch (error) {
                    console.log(error);
                }

                //update react store via reducers
                dispatch({type: CONNECTRTWS, payload: connection});

                //return success to component
                return "Success";
            },
            function (error) {
                console.log(error);
            }
        );
    }
    catch(error){
        console.log(error);
    }
}

