/*
Author: Ethan Qiu
Filename: rtws.js
Last Modified: June 7, 2023
Description: real time websocket reducer
*/

import { CONNECTRTWS } from "../constants/actionTypes";

export default (connection = {}, action) => {
    switch (action.type){
        case CONNECTRTWS:
            return action.payload;
        default:
            return connection;
    }
}