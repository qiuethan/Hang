/*
Author: Ethan Qiu
Filename: chat.js
Last Modified: June 7, 2023
Description: Action methods pertaining to Chat API calls
*/

import { w3cwebsocket as W3CWebSocket } from "websocket";
import * as api from '../api/index.js';

//Constants
import {LOADROOMS, LOADGROUPS, CONNECTWS, BASEWS} from '../constants/actionTypes.js';

//action to load dm rooms from chat api
export const loadrooms = () => async (dispatch) => {
    try{
        //async call to load rooms, stores rooms in data variable
        const { data } = await api.loadrooms();

        //stores data in react store via reducer
        dispatch({ type: LOADROOMS, payload: data });
    }
    catch(error){
        console.log(error)
    }
}

//action to load group rooms from chat api
export const loadgroups = () => async (dispatch) => {
    try{
        //async call to load group rooms, stores rooms in data variable
        const { data } = await api.loadgroups();

        //stores data in react store via reducer
        dispatch({ type: LOADGROUPS, payload: data });
    }
    catch(error){
        console.log(error)
    }
}

//connects websocket to backend
export const connectws = () => (dispatch) => {
    try{

        //define client websocket (sets address)
        let client = JSON.parse(localStorage.getItem('profile')) !== null ? new W3CWebSocket(`${BASEWS}ws/chats/${JSON.parse(localStorage.getItem('profile')).user.username}/`) : null;

        try{
            //when client opens
            client.onopen(() => {
                //authenticate client using token
                client.send(JSON.stringify({
                    action: "authenticate",
                    content: {
                        token: JSON.parse(localStorage.getItem('profile')).token
                    }
                }));

            })
        }
        catch(error){
            console.log(error);
        }

        //when client closes
        client.onclose = (event) => {
            console.log("Client Closed");
        }

        //store client to react store via reducer
        dispatch({ type: CONNECTWS, payload: client});
    }
    catch (error){
        console.log(error);
    }
}

//creates new dm with user
export const createdm = (user) => async(dispatch) => {
    try{
        //async call to create dm, stores data in variable
        const { data } = await api.createdm(user);

        //return data to component
        return data;
    }
    catch(error){
        console.log(error);
    }
}