import { GETSELF } from '../constants/actionTypes.js';

export default (user = [], action) => {
    console.log(action)
    switch (action.type){
        case GETSELF:
            console.log(action.payload);
            return action.payload;
        default:
            return user;
    }
}