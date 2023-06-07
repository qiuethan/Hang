/*
Author: Ethan Qiu
Filename: notifications.js
Last Modified: June 7, 2023
Description: notifications reducer
*/


import { GETUNREADNOTIFICATIONS } from "../constants/actionTypes";

export default (notifications = [], action) => {
    switch (action.type){
        case GETUNREADNOTIFICATIONS:
            return action.payload;
        default:
            return notifications;
    }
}