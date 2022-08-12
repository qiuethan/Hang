import * as api from '../api/index.js'
import { LOGIN, LOGOUT } from '../constants/actionTypes'

export const login = (inputs, router) => async (dispatch) => {
    try{
        const { data } = await api.login(inputs);
        dispatch({ type: LOGIN, data });

        router('/')
    }
    catch(error){
        console.log(error);
        return(error);
    }
}

export const signup = (inputs, router) => async (dispatch) => {
    try{
        const { data } = await api.signin(inputs);
        dispatch({type: LOGIN, data})

        router('/')
    }
    catch (error){
        console.log(error);
    }
}

export const sendemail = (inputs) => async (dispatch) => {
    try{
        const { data } = await api.sendemail(inputs);
    }
    catch(error){
        console.log(error);
    }
}

export const logout = (token) => async(dispatch) => {
    try{
        const res = await api.logout(token);
        dispatch({type: LOGOUT});

        return;
    }
    catch (error){
        console.log(error);
    }
}