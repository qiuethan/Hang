import { ACCEPTFRIENDREQUEST, LOADFRIENDS, REMOVEFRIEND } from "../constants/actionTypes";

export default (friends = [], action) => {
    switch (action.type){
        case LOADFRIENDS:
            return action.payload;
        case ACCEPTFRIENDREQUEST:
            return [...friends, action.payload.user.user.id];
        case REMOVEFRIEND:
            return friends.filter((friend) => friend !== action.payload.friend);
        default: 
            return friends;
    }
}