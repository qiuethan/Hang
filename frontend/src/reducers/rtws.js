import { CONNECTRTWS } from "../constants/actionTypes";

export default (connection = {}, action) => {
    switch (action.type){
        case CONNECTRTWS:
            return action.payload;
        default:
            return connection;
    }
}