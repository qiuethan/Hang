import { LOADRECEIVEDFRIENDREQUESTS, ACCEPTFRIENDREQUEST } from "../constants/actionTypes";

export default (requests = [], action) => {
    switch (action.type){
        case LOADRECEIVEDFRIENDREQUESTS:
            return action.payload;
        case ACCEPTFRIENDREQUEST:
            return requests.filter((request) => request.from_user.id !== action.payload.user.id);
        default: 
            return requests;
    }
}