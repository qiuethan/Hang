/*
Author: Ethan Qiu
Filename: profile.js
Last Modified: June 7, 2023
Description: profile reducer
*/


import { GETSELF } from '../constants/actionTypes.js';

export default (user = [], action) => {
    switch (action.type){
        case GETSELF:
            return action.payload;
        default:
            return user;
    }
}