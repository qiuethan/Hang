import { LOADMESSAGES  } from "../constants/actionTypes";

export default (messages = [], action) => {
    switch (action.type){
        case LOADMESSAGES:
            return action.payload;
        default: 
            return messages;
    }
}