/*
Author: Ethan Qiu
Filename: Navbar.js
Last Modified: June 7, 2023
Description: Display user profile settings
*/

import React, {useEffect, useState} from "react";
import {useDispatch, useSelector} from "react-redux";
import {Box, Button, TextField} from "@mui/material";
import {logout} from "../../../actions/login";
import {getself, updateProfile} from "../../../actions/users";

import "./User.css"
import {useNavigate} from "react-router-dom";

//User component
const User = () => {

    //Define dispatch variable
    const dispatch = useDispatch();

    //Get user from react store
    const user = useSelector(state => state);

    //Define navigation variable
    const navigate = useNavigate();

    //Set edit state variable
    const [edit, setEdit] = useState(false);

    //Set profile fields state variables
    const [picture, setPicture] = useState("");
    const [username, setUsername] = useState("");
    const [aboutMe, setAboutMe] = useState("");
    const [email, setEmail] = useState("");

    //On render
    useEffect(() => {
        //Get self from API
        dispatch(getself());
    }, [])

    //On render + user change
    useEffect(() => {
        try{
            //Set fields to profile fields
            setPicture(user.profile.profile_picture);
            setUsername(user.profile.user.username);
            setAboutMe(user.profile.about_me);
            setEmail(user.profile.user.email);
        }
        catch(error){
            console.log(error);
        }
    }, [user])

    //When user changes image
    const changeImage = (e) => {
        //Allows user to select image, then converts image to DataURL
        const selectedImage = e.target.files[0];
        const reader = new FileReader();
        reader.readAsDataURL(selectedImage);
        reader.onload = () => {
            setPicture(reader.result);
        };
    }

    //Handle About Me Changes
    const changeAboutMe = (e) => {
        e.preventDefault();
        setAboutMe(e.target.value);
    }

    //Handle Whether Edit/View
    const editProfile = (e) => {
        e.preventDefault();
        setEdit(true);
    }

    //Handle when user cancels changes
    const cancel = (e) => {
        e.preventDefault();
        setAboutMe(user.profile.about_me);
        setPicture(user.profile.profile_picture);
        setEdit(false);
    }

    //Handle when user saves changes
    const saveChanges = (e) => {
        e.preventDefault();
        //Send update to API
        dispatch(updateProfile(picture, aboutMe)).then(
            r => {
                //Then get new copy of self
                dispatch(getself());
            }
        );
        setEdit(false);
    }

    //If user presses logout button
    const logOut = (e) => {
        //Dispatch logout to API
        dispatch(logout(JSON.parse(localStorage.getItem("profile")).token)).then((response) => {
            localStorage.clear();
        });
        //Navigate to auth
        navigate("/auth");
    }

    //Render Components
    return(
        <Box sx={{display: "flex", width: "90%", alignSelf: "center", justifyContent: "center", marginBottom: "20px"}}>
                {!edit && (
                    <Box sx={{width: "20%", aspectRatio: "1"}}>
                        {picture && <img style={{display: "block", justifySelf: "center", alignSelf: "center", maxWidth: "100%", maxHeight: "100%", aspectRatio:"1", objectFit: "cover", borderRadius: "50%"}} src={picture} alt="Uploaded Image"/>}
                    </Box>
                )}
                {edit && (
                    <Box sx={{position: "relative", width: "20%", aspectRatio: "1"}}>
                        <label htmlFor="image-input-profile">
                            <Box id="image-profile" sx={{alignItems:"center", justifyContent:"center"}}>
                                {picture && <img style={{display: "block", justifySelf: "center", alignSelf: "center", maxWidth: "100%", maxHeight: "100%", aspectRatio:"1", objectFit: "cover", borderRadius: "50%"}} className="image-profile-preview" src={picture} alt="Uploaded Image"/>}
                                <div className="overlay-profile">
                                    Click To Choose Image
                                </div>
                            </Box>
                        </label>
                        <input
                            type="file"
                            id="image-input-profile"
                            accept="image/*"
                            name="picture"
                            onChange={changeImage}
                            style={{display: "none"}}
                        />
                    </Box>
                )}
            <Box sx={{width: "80%", marginLeft: "10px"}}>
                {!edit && (
                    <Box sx={{display: "flex", flexDirection: "column", height: "100%"}}>
                        <Box sx={{display: "flex", flexDirection: "row", height: "20%"}}>
                            {username}
                        </Box>
                        <Box sx={{display: "flex", height: "20%"}}>
                            {email}
                        </Box>
                        <Box sx={{display: "flex",  height: "60%", width: "100%"}}>
                            <TextField
                                value={aboutMe}
                                style={{width: '90%'}}
                                multiline
                                rows={4}
                            />
                        </Box>
                        <Box sx={{display: "flex", flexDirection: "row", width: "100%"}}>
                            <Button sx={{marginTop: "20px", width: "50%", marginRight: "5px", backgroundColor: "#0c7c59", color: "white", ":hover": {color: "#0c7c59", backgroundColor: "white"}}} onClick={editProfile}>Edit Profile</Button>
                            <Button sx={{marginTop: "20px", width: "50%", marginRight: "5px", backgroundColor: "red", color: "white", ":hover": {color: "red", backgroundColor: "white"}}} onClick={logOut}>Log Out</Button>
                        </Box>
                    </Box>
                )}
                {edit && (
                    <Box sx={{display: "flex", flexDirection: "column", height: "100%"}}>
                        <Box sx={{display: "block", flexDirection: "row", height: "20%"}}>
                            <label style={{marginRight: "5px"}}>Username:</label>
                            {username}
                        </Box>
                        <Box sx={{display: "block", height: "20%"}}>
                            <label style={{marginRight: "5px"}}>Email:</label>
                            {email}
                        </Box>
                        <Box sx={{display: "flex",  height: "50%", width: "100%"}}>
                            <label style={{marginRight: "5px"}}>About Me:</label>
                            <TextField
                                value={aboutMe}
                                onChange={changeAboutMe}
                                style={{width: '90%'}}
                                multiline
                                rows={4}
                            />
                        </Box>
                        <Box sx={{display: "flex", flexDirection: "row", width: "100%"}}>
                            <Button sx={{marginTop: "20px", width: "50%", marginRight: "5px", backgroundColor: "red", color: "white", ":hover": {color: "red", backgroundColor: "white"}}} onClick={cancel}>Cancel Changes</Button>
                            <Button sx={{marginTop: "20px", width: "50%", marginRight: "5px", backgroundColor: "#0c7c59", color: "white", ":hover": {color: "#0c7c59", backgroundColor: "white"}}} onClick={saveChanges}>Save Changes</Button>
                        </Box>
                    </Box>
                )}
            </Box>
        </Box>
    )
}

export default User;