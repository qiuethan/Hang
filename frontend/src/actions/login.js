import * as api from '../api/index.js'
import { LOGIN } from '../constants/actionTypes'

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
        console.log(inputs);
        const { data } = await api.signin(inputs);
        dispatch({type: LOGIN, data})

        router('/')
    }
    catch (error){
        console.log(error);
    }
}