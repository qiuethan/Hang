import React from "react";
import { useState, useEffect } from "react";
import { useDispatch, useSelector } from "react-redux";
import { useNavigate } from 'react-router-dom';

import { login, sendemail, signup } from "../../actions/login.js";

import logo from "../../images/logo.svg";

import Google from './Google/Google';
import {Box, Button, Paper, TextField} from "@mui/material";

const initialState = {username: "", email: "", password: ""};

const Auth = ({currentPage, setCurrentPage}) => {

    const dispatch = useDispatch();
    const history = useNavigate();

    const [inputs, setInputs] = useState(initialState);
    const [isSignup, setIsSignup] = useState(false);
    const [confirm, setConfirm] = useState({confirmPassword: ""})

    const [confirmAccount, setConfirmAccount] = useState(false);

    const navigate = useNavigate();

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
                dispatch(signup(inputs, navigate))
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
                                        <h3 style={{margin: "0", fontSize: "24px", marginBottom: "10px"}}>Username</h3>
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
                                <h3 style={{margin: "0", fontSize: "24px", marginBottom: "10px"}}>Email</h3>
                                <TextField
                                    type="text"
                                    name="email"
                                    value={inputs.email || ""}
                                    onChange = {handleChange}
                                    sx={{width: "100%", bgcolor: "white", borderRadius: "5px", "& .MuiOutlinedInput-root":{"& > fieldset": {border: "none"}}}}
                                />
                            </Box>
                            <Box sx={{width: "100%", display: "flex", flexDirection: "column", alignItems: "center", marginBottom: "20px"}}>
                                <h3 style={{margin: "0", fontSize: "24px", marginBottom: "10px"}}>Password</h3>
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
                                        <h3 style={{margin: "0", fontSize: "24px", marginBottom: "10px"}}>Confirm Password</h3>
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
                                    <Box>
                                        <p style={{color: "black", margin: "0"}}>Email Has Been Sent, Please Verify Account</p>
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