/*
Author: Ethan Qiu
Filename: dms.js
Last Modified: June 7, 2023
Description: dms reducer
*/


import { LOADROOMS } from "../constants/actionTypes";

export default (rooms = [], action) => {
    switch (action.type){
        case LOADROOMS:
            return action.payload;
        default: 
            return rooms;
    }
}