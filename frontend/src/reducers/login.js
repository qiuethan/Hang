/*
Author: Ethan Qiu
Filename: login.js
Last Modified: June 7, 2023
Description: authentication reducer
*/


import * as actionTypes from '../constants/actionTypes';

const authReducer = (state = { authData: null }, action) => {
    switch (action.type){
        case actionTypes.LOGIN:
            localStorage.setItem('profile', JSON.stringify({...action?.data}));

            return {...state, authData: action.data, loading:false, errors:null};
        case actionTypes.LOGOUT:
            localStorage.clear();

            return{...state, authData:null, loading: false, errors: null};
        default:
            return state;
    }
}

export default authReducer;