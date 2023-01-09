import { CREATEHANGEVENT, GETHANGEVENTS } from "../constants/actionTypes"

export default (hangs = [], action) => {
    switch(action.type){
        case CREATEHANGEVENT:
            return hangs
        case GETHANGEVENTS:
            if(action.payload !== undefined){
                return action.payload;
            }
            else{
                return hangs;
            }
        default:
            return hangs;
    }
}