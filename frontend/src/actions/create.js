import * as api from '../api/index.js';

import { CREATEHANGEVENT } from '../constants/actionTypes.js'

export const createhangevent = (inputs) => async(dispatch) => {
    try{
        const { data } = await api.createhangevent(inputs);
        dispatch({type: CREATEHANGEVENT, payload: data})
    }
    catch (error){
        console.log(error);
    }
}