import * as api from '../api/index.js';
import { LOADFRIENDS, LOADRECEIVEDFRIENDREQUESTS, ACCEPTFRIENDREQUEST } from '../constants/actionTypes.js';

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