import * as api from '../api/index.js';
import { LOADMESSAGES } from '../constants/actionTypes.js';

export const loadmessages = (room) => async (dispatch) => {
    try{
        const { data } = await api.loadMessage(room);
        dispatch({ type: LOADMESSAGES, payload: data });
    }
    catch(error){
        console.log(error)
    }
}