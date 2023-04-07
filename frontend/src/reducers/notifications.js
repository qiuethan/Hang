import { GETUNREADNOTIFICATIONS } from "../constants/actionTypes";

export default (notifications = [], action) => {
    switch (action.type){
        case GETUNREADNOTIFICATIONS:
            console.log(action.payload);
            return action.payload;
        default:
            return notifications;
    }
}