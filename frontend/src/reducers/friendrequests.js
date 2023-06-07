/*
Author: Ethan Qiu
Filename: friendrequests.js
Last Modified: June 7, 2023
Description: friend request reducer
*/


import { LOADRECEIVEDFRIENDREQUESTS, ACCEPTFRIENDREQUEST, DECLINEFRIENDREQUEST } from "../constants/actionTypes";

export default (requests = [], action) => {
    switch (action.type){
        case LOADRECEIVEDFRIENDREQUESTS:
            return action.payload;
        case ACCEPTFRIENDREQUEST:
            return requests.filter((request) => request.from_user.id !== action.payload.user.id);
        case DECLINEFRIENDREQUEST:
            return requests.filter((request) => request.from_user.id !== action.payload.user.id);
        default: 
            return requests;
    }
}