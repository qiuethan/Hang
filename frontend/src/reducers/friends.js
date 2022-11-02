import { ACCEPTFRIENDREQUEST, LOADFRIENDS, REMOVEFRIEND } from "../constants/actionTypes";

export default (friends = [], action) => {
    switch (action.type){
        case LOADFRIENDS:
            return action.payload;
        case ACCEPTFRIENDREQUEST:
            return [...friends, action.payload.user];    
        case REMOVEFRIEND:
            return friends.filter((friend) => friend.id !== action.payload.friend.id);
        default: 
            return friends;
    }
}