/*
Author: Ethan Qiu
Filename: hangs.js
Last Modified: June 7, 2023
Description: hang events reducer
*/


import { CREATEHANGEVENT, GETHANGEVENTS } from "../constants/actionTypes"

export default (hangs = [], action) => {
    switch(action.type){
        case CREATEHANGEVENT:
            return hangs
        case GETHANGEVENTS:
            if(action.payload !== undefined){
                return action.payload;
            }
            else{
                return hangs;
            }
        default:
            return hangs;
    }
}