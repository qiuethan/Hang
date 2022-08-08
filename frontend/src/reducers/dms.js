import { LOADROOMS } from "../constants/actionTypes";

export default (rooms = [], action) => {
    switch (action.type){
        case LOADROOMS:
            return action.payload;
        default: 
            return rooms;
    }
}