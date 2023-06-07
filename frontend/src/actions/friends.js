/*
Author: Ethan Qiu
Filename: friends.js
Last Modified: June 7, 2023
Description: Action methods pertaining to Friends API calls
*/

import * as api from '../api/index.js';
import { LOADFRIENDS, LOADRECEIVEDFRIENDREQUESTS, ACCEPTFRIENDREQUEST, DECLINEFRIENDREQUEST, REMOVEFRIEND, BLOCKFRIEND, LOADSENTFRIENDREQUESTS, DELETESENTFRIENDREQUEST, LOADBLOCKEDUSERS, UNBLOCKUSER } from '../constants/actionTypes.js';

import {getuserbyemail} from "./users";

//action to load friends from friends api
export const loadfriends = () => async(dispatch) => {
    try{
        //async call, stores return in variable
        const { data } = await api.loadfriends();

        //stores data in react store via reducer
        dispatch({ type: LOADFRIENDS, payload: data });

    }
    catch(error){
        console.log(error);
    }
} 

//action to load recieved friend requests from friends API
export const loadrecievedfriendrequests = () => async(dispatch) => {
    try{
        //async call, stores return in variable
        const { data } = await api.loadrecievedfriendrequests();

        //stores data in react store via reducer
        dispatch({ type: LOADRECEIVEDFRIENDREQUESTS, payload: data});
    }
    catch (error){
        console.log(error);
    }
}

//action to accept friend request using friends API
export const acceptfriendrequest = (user) => async(dispatch) => {
    try{

        //async function to send acceptance to server
        await api.acceptfriendrequest(user.user.id);

        //updating react store via reducer
        dispatch({ type: ACCEPTFRIENDREQUEST, payload: { user } });
    }
    catch(error){
        console.log(error);
    }
}

//action to decline friend request using friends API
export const declinefriendrequest = (user) => async(dispatch) => {
    try{
        //async function to send decline to server
        await api.declinefriendrequest(user.user.id);

        //updating react store via reducer
        dispatch({ type: DECLINEFRIENDREQUEST, payload: { user }})
    }
    catch(error){
        console.log(error)
    }
}

//action to remove friend using friends API
export const removefriend = (friend) => async(dispatch) => {
    try{
        //async function to send removal to server
        await api.removefriend(friend);

        //updating react store via reducer
        dispatch({ type: REMOVEFRIEND, payload: { friend }})
    }
    catch(error){
        console.log(error);
    }
}

//action to block friend using friends API
export const blockfriend = (friend) => async(dispatch) => {
    try{

        //async call to backend to block friend
        await api.blockfriend(friend);

        //async call to backend to remove friend
        await api.removefriend(friend);

        //reflect changes in react store via reducer
        dispatch({ type: REMOVEFRIEND, payload: { friend }})
        dispatch({ type: BLOCKFRIEND, payload: { friend }})
    }
    catch(error){
        console.log(error);
    }
}

//action to send friend request using friends API
export const sendfriendrequest = (email) => async(dispatch) => {
    try{
        //get user via email
        const user = await dispatch(getuserbyemail(email));

        //using user, send friend request to API
        await api.sendfriendrequest(user.user.id);
    }
    catch(error){
        console.log(error);
    }
}

//action to load sent friend requests using friends API
export const loadsentfriendrequests = () => async(dispatch) => {
    try{
        //store return values in variable
        const { data } = await api.loadsentfriendrequests();

        //update react store via reducers
        dispatch({type : LOADSENTFRIENDREQUESTS, payload: data});
    }
    catch(error){
        console.log(error);
    }
}

//action to load blocked users using friends API
export const loadblockedusers = () => async(dispatch) => {
    try{
        //return value stored as variable
        const { data } = await api.loadblockedusers();

        //update react store via reducers
        dispatch({type: LOADBLOCKEDUSERS, payload: data})
    }
    catch(error){
        console.log(error);
    }
}

//action to unblock user using friends API
export const unblockeduser = (id) => async(dispatch) => {
    try{
        //call to backend to unblock user
        await api.unblockuser(id);

        //update react store via reducers
        dispatch({type: UNBLOCKUSER, payload: {id}})
    }
    catch(error){
        console.log(error);
    }
}

//action to delete sent friend request using friends API
export const deletesentfriendrequest = (id) => async(dispatch) => {
    try{
        //call to backend to delete sent friend request
        await api.deletesentfriendrequest(id);

        //update react store via reducers
        dispatch({type: DELETESENTFRIENDREQUEST, payload: {id}})
    }
    catch(error){
        console.log(error);
    }
}