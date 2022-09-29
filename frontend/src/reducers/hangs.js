import { CREATEHANGEVENT } from "../constants/actionTypes"

export default (hangs = [], action) => {
    switch(action.type){
        case CREATEHANGEVENT:
            return hangs
        default:
            return hangs
    }
}