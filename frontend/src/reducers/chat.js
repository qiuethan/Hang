import { LOADROOMS } from "../constants/actionTypes";

export default (messages = [], action) => {
    switch (action.type){
        case LOADROOMS:
            return action.payload;
        default: 
            return messages;
    }
}