import * as api from '../api/index.js';

import { CREATEHANGEVENT, GETHANGEVENTS } from '../constants/actionTypes.js'

export const createhangevent = (inputs) => async(dispatch) => {
    try{
        console.log(inputs);
        const { data } = await api.createhangevent(inputs);
        dispatch({type: CREATEHANGEVENT, payload: data})
    }
    catch (error){
        console.log(error);
    }
}

export const gethangevents = () => async(dispatch) => {
    try{
        const { data } = await api.gethangevents();
        dispatch({type: GETHANGEVENTS, payload: data})
    }
    catch(error){
        console.log(error);
    }
}

export const joinhangevent = (code, navigate) => async(dispatch) => {
    try{
        const { data } = await api.joinhangevent();
        console.log(data);
        navigate(`/hang/?room=${data.id}`)
    }
    catch(error){
        console.log(error);
    }
}