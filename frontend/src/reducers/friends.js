import { ACCEPTFRIENDREQUEST, LOADFRIENDS } from "../constants/actionTypes";

export default (friends = [], action) => {
    switch (action.type){
        case LOADFRIENDS:
            return action.payload;
        case ACCEPTFRIENDREQUEST:
            return [...friends, action.payload.user];        
        default: 
            return friends;
    }
}