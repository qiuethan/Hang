import * as api from '../api/index.js';

import {GETUSER} from '../constants/actionTypes.js'

export const getuser = (id) => async(dispatch) => {
    try{
        const { data } = await api.getuser(id);

        dispatch({ type: GETUSER, payload: data })
    }
    catch(error){
        console.log(error)
    }
};
