import { BLOCKFRIEND } from "../constants/actionTypes";

export default (blocked = [], action) => {
    switch (action.type){
        case BLOCKFRIEND:
            console.log(action.payload.friend)
            return [...blocked, action.payload.friend];
        default: 
            return blocked;
    }
}