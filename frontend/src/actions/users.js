import * as api from '../api/index.js';

import {GETUSER} from '../constants/actionTypes.js'

export const getuser = (id) => async(dispatch) => {
    try{
        const { data } = await api.getuser(id);

        dispatch({ type: GETUSER, payload: data })

        return data;
    }
    catch(error){
        console.log(error)
    }
};

export const getuserbyusername = (username) => async(dispatch) => {
    try{
        const { data } = await api.getuserbyusername(username);

        dispatch({ type: GETUSER, payload: data })

        return data;
    }
    catch(error){
        console.log(error);
    }
}

export const getuserbyemail = (email) => async(dispatch) => {
    try{
        const { data } = await api.getuserbyemail(email);

        console.log(data);

        dispatch({ type: GETUSER, payload: data })

        return data;
    }
    catch(error){
        console.log(error);
    }
}