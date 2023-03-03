import {connection} from '../api/ws';
import {CONNECTRTWS} from "../constants/actionTypes";

export const connectRTWS = () => (dispatch) => {
    try{
        try{
            connection.send(JSON.stringify({
                action: "authenticate",
                content: {
                    token: JSON.parse(localStorage.getItem('profile')).token
                }
            }));
        }
        catch(error){
            console.log(error);
        }

        dispatch({ type: CONNECTRTWS, payload: connection});
    }
    catch (error){
        console.log(error);
    }
}

export const pingRTWS = (dispatch) => {
    try{
        connection.send(JSON.stringify({
            action: "ping",
            content: {}
        }))
    }
    catch (error){
        console.log(error)
    }
}