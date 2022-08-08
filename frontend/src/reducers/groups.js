import { LOADGROUPS } from "../constants/actionTypes";

export default (rooms = [], action) => {
    switch (action.type){
        case LOADGROUPS:
            return action.payload;
        default: 
            return rooms;
    }
}