/*
Author: Ethan Qiu
Filename: Auth.js
Last Modified: June 7, 2023
Description: Authenticates the user
*/

import React from "react";
import { useState, useEffect } from "react";
import { useDispatch, useSelector } from "react-redux";
import { useNavigate } from 'react-router-dom';
import { login, sendemail, signup } from "../../actions/login.js";
import logo from "../../images/logo.svg";
import Google from './Google/Google';
import {Box, Button, Paper, TextField} from "@mui/material";

const initialState = {username: "", email: "", password: ""};

// functional component for the authentication page.
// currentPage and setCurrentPage are passed as props from the parent component.
const Auth = ({currentPage, setCurrentPage}) => {

    // Setting up Redux's useDispatch hook to dispatch actions.
    const dispatch = useDispatch();

    // Setting up the react-router-dom hook to navigate between pages.
    const history = useNavigate();

    // Setting up the local state using the useState hook.
    const [inputs, setInputs] = useState(initialState);
    const [isSignup, setIsSignup] = useState(false);
    const [confirm, setConfirm] = useState({confirmPassword: ""})
    const [confirmAccount, setConfirmAccount] = useState(false);

    // Setting up error checking
    const [error, setError] = useState("");

    // We are using react-router-dom's navigate hook to navigate programmatically.
    const navigate = useNavigate();

    // Using the useEffect hook to perform side effects, i.e. effects that happen outside of the return method.
    useEffect(() => {
        setCurrentPage("auth")
        if(JSON.parse(localStorage.getItem('profile')) !== null){
            history('/');
        }
    }, [useSelector((state) => state)])

    // handle input changes for the form fields
    const handleChange = (event) => {
        const name = event.target.name;
        const value = event.target.value;
        setInputs(values => ({...values, [name] : value}));
    }

    // handle form submission
    const handleSubmit = (event) => {
        event.preventDefault();

        if(isSignup){
            if(inputs.password === confirm.confirmPassword){
                dispatch(signup(inputs, navigate)) // dispatches signup action
                    .then((response) => {
                        if(response === undefined){
                            window.location.reload();
                        }
                        try{
                            //Handle non-field errors
                            handleErrors(response.response.data.non_field_errors);
                        }
                        catch (error){
                            console.log(response);
                            //Handle Field Errors
                            try{
                                if(response.response.data.email !== undefined){
                                    setError("Email: " + response.response.data.email)
                                }
                                else if(response.response.data.username !== undefined){
                                    setError("Username: " + response.response.data.username)
                                }
                                else if(response.response.data.password !== undefined){
                                    setError("Password: " + response.response.data.password);
                                }
                            }
                            catch(e){
                                console.log(e);
                            }
                        }
                    });
            }
            else{
                console.log("Passwords don't match.")
            }
        }
        else{
            dispatch(login(inputs)) // dispatches login action
                .then((response) => {
                    try{
                        handleErrors(response.response.data);
                    }
                    catch (error){
                        try{
                            if(response.response.data.email !== undefined){
                                setError("Email: " + response.response.data.email)
                            }
                            else if(response.response.data.password !== undefined){
                                setError("Password: " + response.response.data.password);
                            }
                        }
                        catch(e){
                            console.log(e);
                        }
                    }
                })
        }
    }

    // handle error messages from server
    const handleErrors = (response) => {
        if(response.non_field_errors !== undefined){
            if(response.non_field_errors[0] == "User is not verified."){
                setConfirmAccount(true);
                sendVerificationEmail();
            }
            else{
                setError(response.non_field_errors[0]);
            }
        }
    }

    // sending verification email
    const sendVerificationEmail = () => {
        dispatch(sendemail(inputs));
        setInputs(initialState);
    }

    // handle input changes for the confirm password field
    const confirmHandleChange = (event) => {
        const name = event.target.name;
        const value = event.target.value;
        setConfirm(values => ({...values, [name] : value}));
    }

    // switching between sign up and login mode
    const switchMode = () => {
        setInputs(initialState);
        setIsSignup((prevIsSignup) => !prevIsSignup);
    }

    // Render authentication form

    return(
        <Box sx={{display: "flex", width: "100%", height: '100%', alignItems: "center", justifyContent: "center"}}>
            <Paper elevation={16} sx={{width: "70%", height: "90%", borderRadius: "10px", display: "flex", alignItems: "center", justifyContent: "center", bgcolor: "#a5d6b0"}}>
                <Box sx={{width: "90%", height: "90%", display: "flex", flexDirection: "row"}}>
                    <Box sx={{width: "50%", height: "100%", marginRight: "10px", display: "flex", alignItems: "center", justifyContent: "center"}}>
                        <img src={logo}/>
                    </Box>
                    <Box sx={{width: "50%", height: "100%", marginLeft: "10px", display: "flex", flexDirection: "column"}}>

                        <form onSubmit={handleSubmit} class="signin-form">

                            {
                                isSignup && (
                                    <Box sx={{width: "100%", display: "flex", flexDirection: "column", alignItems: "center", marginBottom: "20px"}}>
                                        <h4 style={{margin: "0", fontSize: "20px", marginBottom: "10px"}}>Username</h4>
                                        <TextField
                                            type="text"
                                            name="username"
                                            value={inputs.username || ""}
                                            onChange = {handleChange}
                                            sx={{width: "100%", bgcolor: "white", borderRadius: "5px", "& .MuiOutlinedInput-root":{"& > fieldset": {border: "none"}}}}
                                        />
                                    </Box>
                                )
                            }
                            <Box sx={{width: "100%", display: "flex", flexDirection: "column", alignItems: "center", marginBottom: "20px"}}>
                                <h4 style={{margin: "0", fontSize: "20px", marginBottom: "10px"}}>Email</h4>
                                <TextField
                                    type="text"
                                    name="email"
                                    value={inputs.email || ""}
                                    onChange = {handleChange}
                                    sx={{width: "100%", bgcolor: "white", borderRadius: "5px", "& .MuiOutlinedInput-root":{"& > fieldset": {border: "none"}}}}
                                />
                            </Box>
                            <Box sx={{width: "100%", display: "flex", flexDirection: "column", alignItems: "center", marginBottom: "20px"}}>
                                <h4 style={{margin: "0", fontSize: "20px", marginBottom: "10px"}}>Password</h4>
                                <TextField
                                    type="password"
                                    name="password"
                                    value={inputs.password || ""}
                                    onChange = {handleChange}
                                    sx={{width: "100%", bgcolor: "white", borderRadius: "5px", "& .MuiOutlinedInput-root":{"& > fieldset": {border: "none"}}}}
                                />
                            </Box>
                            {
                                isSignup && (
                                    <Box sx={{width: "100%", display: "flex", flexDirection: "column", alignItems: "center", marginBottom: "20px"}}>
                                        <h4 style={{margin: "0", fontSize: "20px", marginBottom: "10px"}}>Confirm Password</h4>
                                        <TextField
                                            type="password"
                                            name="confirmPassword"
                                            value={confirm.confirmPassword || ""}
                                            onChange = {confirmHandleChange}
                                            sx={{width: "100%", bgcolor: "white", borderRadius: "5px", "& .MuiOutlinedInput-root":{"& > fieldset": {border: "none"}}}}
                                        />
                                    </Box>
                                )
                            }

                            {
                                confirmAccount && (
                                    <Box sx={{width: "100%", display: "flex", justifyContent: "center", alignItems: "center", marginBottom: "20px"}}>
                                        <p style={{color: "black", margin: "0"}}>Verification Sent. Please Check Your Email.</p>
                                    </Box>
                                )
                            }

                            {
                                error !== "" && (
                                    <Box sx={{width: "100%", display: "flex", justifyContent: "center", alignItems: "center", marginBottom: "20px"}}>
                                        <p style={{color: "black", margin: "0"}}>{error}</p>
                                    </Box>
                                )
                            }

                            <Button disableRipple sx={{bgcolor: "#0c7c59", width: "100%", color: "white", marginBottom: "10px", ":hover": {color: "black"}}} type="submit">{isSignup ? 'Sign Up' : "Login"}</Button>
                        </form>

                        {!isSignup && (
                            <Google/>
                        )}

                        <Button onClick={switchMode} disableRipple sx={{bgcolor: "#0c7c59", color: "white", marginBottom: "10px", ":hover": {color: "black"}}}>
                            {isSignup ? 'Already have an account? Log in!' : "Don't have an account? Sign Up!"}
                        </Button>

                    </Box>
                </Box>
            </Paper>
        </Box>
    );

}

export default Auth;