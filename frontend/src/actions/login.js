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

export const logout = (token) => async(dispatch) => {
    try{
        const res = await api.logout(token);
        dispatch({type: LOGOUT});
    }
    catch (error){
        console.log(error);
    }
}