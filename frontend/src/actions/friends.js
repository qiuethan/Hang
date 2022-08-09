import * as api from '../api/index.js';
import { LOADFRIENDS } from '../constants/actionTypes.js';

export const loadfriends = () => async(dispatch) => {
    try{
        const { data } = await api.loadfriends();
        dispatch({ type: LOADFRIENDS, payload: data });

    }
    catch(error){
        console.log(error);
    }
} 