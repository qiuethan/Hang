/*
Author: Ethan Qiu
Filename: sentrequests.js
Last Modified: June 7, 2023
Description: sent friend requests reducer
*/

import { LOADSENTFRIENDREQUESTS, DELETESENTFRIENDREQUEST } from "../constants/actionTypes";

export default (sentrequests = [], action) => {
    switch (action.type){
        case LOADSENTFRIENDREQUESTS:
            return action.payload;
        case DELETESENTFRIENDREQUEST:
            return sentrequests.filter((request) => request.to_user !== action.payload.id);
        default:
            return sentrequests;
    }
}