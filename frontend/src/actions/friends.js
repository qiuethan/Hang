import * as api from '../api/index.js';
import { LOADFRIENDS, LOADRECEIVEDFRIENDREQUESTS, ACCEPTFRIENDREQUEST, DECLINEFRIENDREQUEST, REMOVEFRIEND, BLOCKFRIEND } from '../constants/actionTypes.js';

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
        await api.acceptfriendrequest(user.id);

        dispatch({ type: ACCEPTFRIENDREQUEST, payload: { user } });
    }
    catch(error){
        console.log(error);
    }
}

export const declinefriendrequest = (user) => async(dispatch) => {
    try{
        await api.declinefriendrequest(user.id);

        dispatch({ type: DECLINEFRIENDREQUEST, payload: { user }})
    }
    catch(error){
        console.log(error);
    }
}

export const removefriend = (friend) => async(dispatch) => {
    try{
        await api.removefriend(friend.id);

        dispatch({ type: REMOVEFRIEND, payload: { friend }})
    }
    catch(error){
        console.log(error);
    }
}

export const blockfriend = (friend) => async(dispatch) => {
    try{
        await api.blockfriend(friend.id);
        await api.removefriend(friend.id);

        dispatch({ type: REMOVEFRIEND, payload: { friend }})
        dispatch({ type: BLOCKFRIEND, payload: { friend }})
    }
    catch(error){
        console.log(error);
    }
}

export const sendfriendrequest = (email) => async(dispatch) => {
    try{
        await api.sendfriendrequest(email);
    }
    catch(error){
        console.log(error);
    }
}