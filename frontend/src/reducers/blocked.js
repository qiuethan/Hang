/*
Author: Ethan Qiu
Filename: blocked.js
Last Modified: June 7, 2023
Description: blocked users reducer
*/

import { BLOCKFRIEND, LOADBLOCKEDUSERS, UNBLOCKUSER } from "../constants/actionTypes";

export default (blocked = [], action) => {
    switch (action.type){
        case LOADBLOCKEDUSERS:
            return action.payload;
        case BLOCKFRIEND:
            console.log(action.payload.friend)
            return [...blocked, action.payload.friend];
        case UNBLOCKUSER:
            return blocked.filter((blocked) => blocked.id !== action.payload.friend);
        default: 
            return blocked;
    }
}