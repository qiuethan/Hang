import * as api from '../api/index.js';
import { LOADFRIENDS, LOADRECEIVEDFRIENDREQUESTS, ACCEPTFRIENDREQUEST, DECLINEFRIENDREQUEST, REMOVEFRIEND, BLOCKFRIEND } from '../constants/actionTypes.js';

import {getuserbyemail} from "./users";

export const loadfriends = () => async(dispatch) => {
    try{
        const { data } = await api.loadfriends();
        dispatch({ type: LOADFRIENDS, payload: data });

    }
    catch(error){
        console.log(error);
    }
} 

export const loadrecievedfriendrequests = () => async(dispatch) => {
    try{
        const { data } = await api.loadrecievedfriendrequests();

        dispatch({ type: LOADRECEIVEDFRIENDREQUESTS, payload: data});
    }
    catch (error){
        console.log(error);
    }
}

export const acceptfriendrequest = (user) => async(dispatch) => {
    try{
        console.log(user.user.id);
        await api.acceptfriendrequest(user.user.id);

        dispatch({ type: ACCEPTFRIENDREQUEST, payload: { user } });
    }
    catch(error){
        console.log(error);
    }
}

export const declinefriendrequest = (user) => async(dispatch) => {
    try{
        await api.declinefriendrequest(user.user.id);

        dispatch({ type: DECLINEFRIENDREQUEST, payload: { user }})
    }
    catch(error){
        console.log(error);
    }
}

export const removefriend = (friend) => async(dispatch) => {
    try{
        await api.removefriend(friend);

        dispatch({ type: REMOVEFRIEND, payload: { friend }})
    }
    catch(error){
        console.log(error);
    }
}

export const blockfriend = (friend) => async(dispatch) => {
    try{
        await api.blockfriend(friend);
        await api.removefriend(friend);

        dispatch({ type: REMOVEFRIEND, payload: { friend }})
        dispatch({ type: BLOCKFRIEND, payload: { friend }})
    }
    catch(error){
        console.log(error);
    }
}

export const sendfriendrequest = (email) => async(dispatch) => {
    try{
        console.log(email);
        const user = await dispatch(getuserbyemail(email));
        await api.sendfriendrequest(user.user.id);
    }
    catch(error){
        console.log(error);
    }
}