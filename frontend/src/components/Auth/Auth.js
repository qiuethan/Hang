import React from "react";
import { useState } from "react";
import { ReactDOM } from "react";
import './Auth.css';
import { useDispatch, useSelector } from "react-redux";
import { useNavigate } from 'react-router-dom';
import { GoogleLogin } from 'react-google-login';

import { login } from "../../actions/login.js";

const initialState = {email: "", password: ""};

const Auth = (props) => {

    const dispatch = useDispatch();
    const history = useNavigate();

    const [inputs, setInputs] = useState(initialState);
    const [isSignup, setIsSignup] = useState(false);


    const handleChange = (event) => {
        const name = event.target.name;
        const value = event.target.value;
        setInputs(values => ({...values, [name] : value}));
    }

    const handleSubmit = (event) => {
        event.preventDefault();

        dispatch(login(inputs, history));
    }

    const switchMode = () => {
        setForm(initialState);
        setIsSignup((prevIsSignup) => !prevIsSignup);
    }

    const googleSuccess = async(res) => {
        const result = res?.profileObj;
        const token = res?.tokenId;

        try{
            dispatch({type: Auth, data: {result, token}});
            
            history('/');
        } catch (error){
            console.log(error);
        }
    };

    const googleError = () => alert('Google login was unsuccessful. Try again later');

    return(
        <form onSubmit={handleSubmit} class = "signin-form">
            <label>
                Email:
                <input
                    type="text"
                    name="email"
                    placeholder="Email"
                    value={inputs.email || ""}
                    onChange = {handleChange}
                />
            </label>
            <label>
                Password:
                <input
                    type="password"
                    name="password"
                    placeholder="Password"
                    value={inputs.password || ""}
                    onChange = {handleChange}
                />
            </label>
            <button type="submit">Login</button>
            <GoogleLogin 
                clientId="791387321453-ieduv1tkctrh201givjd67kal9uc70ql.apps.googleusercontent.com"
                buttonText="Login with Google"
                onSuccess={googleSuccess}
                onFailure={googleError}
                isSignedIn={true}
                cookiePolicy={'single_host_origin'}
            />
        </form>
    );

}

export default Auth;