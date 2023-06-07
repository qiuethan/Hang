/*
Author: Ethan Qiu
Filename: users.js
Last Modified: June 7, 2023
Description: users reducer
*/

import { GETUSER } from '../constants/actionTypes.js';

export default (users = [], action) => {
    switch (action.type){
        case GETUSER:
            if((users.find((user) => user.user.id === action.payload.user.id)) == undefined){
                return [...users, action.payload];
            }
            else{
                return users;
            }
        default:
            return users;
    }
}