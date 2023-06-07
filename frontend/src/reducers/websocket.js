/*
Author: Ethan Qiu
Filename: websocket.js
Last Modified: June 7, 2023
Description: chat websocket reducer
*/

import { CONNECTWS } from "../constants/actionTypes";

export default (client = {}, action) => {
    switch (action.type){
        case CONNECTWS:
            return action.payload;
        default: 
            return client;
    }
}