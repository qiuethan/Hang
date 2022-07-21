import * as api from '../api/index.js';
import { client } from '../api/ws.js';

import { LOADROOMS, CONNECTWS } from '../constants/actionTypes.js';

export const loadrooms = () => async (dispatch) => {
    try{
        const { data } = await api.loadrooms();

        dispatch({ type: LOADROOMS, payload: data });
    }
    catch(error){
        console.log(error)
    }
}

export const connectws = () => (dispatch) => {
    try{

        dispatch({ type: CONNECTWS, payload: client});
    }
    catch (error){
        console.log(error);
    }
}