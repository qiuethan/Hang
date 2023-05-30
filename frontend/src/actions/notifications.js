import { w3cwebsocket as W3CWebSocket } from "websocket";
import * as api from "../api/index.js";
import {CONNECTRTWS, GETUNREADNOTIFICATIONS} from "../constants/actionTypes";

export const getUnreadNotifications = () => async(dispatch) => {
    try{
        const {data} = await api.getunreadnotifications();
        console.log(data);
        dispatch({type: GETUNREADNOTIFICATIONS, payload: data});
    }
    catch(error){
        console.log(error);
    }
}

const connect = new Promise(function(success, failure) {
    try{
        let connection = JSON.parse(localStorage.getItem('profile')) !== null ? new W3CWebSocket(`wss://hang-backend.fly.dev/ws/real_time_ws/${JSON.parse(localStorage.getItem('profile')).user.username}/`) : null;
        connection.onopen = () => success(connection);
        connection.onerror = () => failure();
    }
    catch(error){
        failure();
    }
});

export const connectRTWS = () => (dispatch) => {
    try {

        connect.then(
            function (connection) {
                try {
                    connection.send(JSON.stringify({
                        action: "authenticate",
                        content: {
                            token: JSON.parse(localStorage.getItem('profile')).token
                        }
                    }));
                } catch (error) {
                    console.log(error);
                }

                dispatch({type: CONNECTRTWS, payload: connection});

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

