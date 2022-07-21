import { CONNECTWS } from "../constants/actionTypes";

export default (client = {}, action) => {
    switch (action.type){
        case CONNECTWS:
            return action.payload;
        default: 
            return client;
    }
}