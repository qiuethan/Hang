import React from "react";
import { useState, useEffect } from "react";
import { useDispatch, useSelector } from "react-redux";
import { useNavigate } from 'react-router-dom';

import { login, sendemail, signup } from "../../actions/login.js";

import Google from './Google/Google';

const initialState = {username: "", email: "", password: ""};

const Auth = ({currentPage, setCurrentPage}) => {

    const dispatch = useDispatch();
    const history = useNavigate();

    const [inputs, setInputs] = useState(initialState);
    const [isSignup, setIsSignup] = useState(false);
    const [confirm, setConfirm] = useState({confirmPassword: ""})

    const [confirmAccount, setConfirmAccount] = useState(false);

    useEffect(() => {
        setCurrentPage("auth")
        if(JSON.parse(localStorage.getItem('profile')) !== null){
            history('/');
        }
    }, [useSelector((state) => state)])

    const handleChange = (event) => {
        const name = event.target.name;
        const value = event.target.value;
        setInputs(values => ({...values, [name] : value}));
    }

    const handleSubmit = (event) => {
        event.preventDefault();

        if(isSignup){
            if(inputs.password == confirm.confirmPassword){  
                dispatch(signup(inputs))
                .then((response) => {
                    try{
                        handleErrors(response.response.data.non_field_errors);
                    }
                    catch (error){
                        window.location.reload();
                    }
                });
            }
            else{
                console.log("Passwords don't match.")
            }
        }
        else{
            dispatch(login(inputs))
            .then((response) => {
                try{
                    handleErrors(response.response.data);
                }
                catch (error){
                    console.log(error);
                    window.location.reload();
                }
            })
        }
    }

    const handleErrors = (response) => {
        if(response.non_field_errors !== undefined){
            if(response.non_field_errors[0] == "User is not verified."){
                setConfirmAccount(true);
                sendVerificationEmail();
            }
        }
    }

    const sendVerificationEmail = () => {
        dispatch(sendemail(inputs));
        setInputs(initialState);
    }

    const confirmHandleChange = (event) => {
        const name = event.target.name;
        const value = event.target.value;
        setConfirm(values => ({...values, [name] : value}));
    }

    const switchMode = () => {
        setInputs(initialState);
        setIsSignup((prevIsSignup) => !prevIsSignup);
    }

    return(
        <div>
            {
                confirmAccount && (
                    <div>
                        Email Has Been Sent, Please Verify Account 
                    </div>
                )
            }

            <form onSubmit={handleSubmit} class = "signin-form">
            {
                isSignup && (
                    <label>
                        Username:
                        <input 
                            type="text" 
                            name="username" 
                            value={inputs.username || ""} 
                            onChange={handleChange} />
                    </label>
                )
            }
            <label>
                Email:
                <input
                    type="text"
                    name="email"
                    value={inputs.email || ""}
                    onChange = {handleChange}
                />
            </label>
            <label>
                Password:
                <input
                    type="password"
                    name="password"
                    value={inputs.password || ""}
                    onChange = {handleChange}
                />
            </label>
            {
                isSignup && (
                    <label>
                        Confirm Password:
                        <input 
                            type="password" 
                            name="confirmPassword" 
                            value={confirm.confirmPassword || ""} 
                            onChange={confirmHandleChange} />
                    </label>
                )
            }



            <button type="submit">{isSignup ? 'Sign Up' : "Login"}</button>
            </form>
            <button onClick={switchMode}>
                {isSignup ? 'Already have an account? Log in!' : "Don't have an account? Sign Up!"}
            </button>

            {!isSignup && (
                <Google/>
            )}
        </div>
    );

}

export default Auth;