import { LOADFRIENDS } from "../constants/actionTypes";

export default (friends = [], action) => {
    switch (action.type){
        case LOADFRIENDS:
            return action.payload;
        default: 
            return friends;
    }
}