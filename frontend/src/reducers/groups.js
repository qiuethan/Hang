/*
Author: Ethan Qiu
Filename: groups.js
Last Modified: June 7, 2023
Description: group rooms reducer
*/


import { LOADGROUPS } from "../constants/actionTypes";

export default (rooms = [], action) => {
    switch (action.type){
        case LOADGROUPS:
            return action.payload;
        default: 
            return rooms;
    }
}