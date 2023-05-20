import { LOADSENTFRIENDREQUESTS, DELETESENTFRIENDREQUEST } from "../constants/actionTypes";

export default (sentrequests = [], action) => {
    switch (action.type){
        case LOADSENTFRIENDREQUESTS:
            return action.payload;
        case DELETESENTFRIENDREQUEST:
            console.log(action.payload.id);
            console.log(sentrequests);
            return sentrequests.filter((request) => request.to_user !== action.payload.id);
        default:
            return sentrequests;
    }
}