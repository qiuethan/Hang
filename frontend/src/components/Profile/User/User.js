import React, {useEffect, useState} from "react";
import {useDispatch, useSelector} from "react-redux";
import {Box, Button, TextField} from "@mui/material";
import {getself, updateProfile} from "../../../actions/users";

import FileBase from 'react-file-base64';

import "./User.css"

const User = () => {


    const dispatch = useDispatch();
    const user = useSelector(state => state);

    console.log(user.profile);

    const [edit, setEdit] = useState(false);

    const [picture, setPicture] = useState("");
    const [username, setUsername] = useState("");
    const [aboutMe, setAboutMe] = useState("");
    const [email, setEmail] = useState("");

    useEffect(() => {
        dispatch(getself());
    }, [])

    useEffect(() => {
        try{
            setPicture(user.profile.profile_picture);
            setUsername(user.profile.user.username);
            setAboutMe(user.profile.about_me);
            setEmail(user.profile.user.email);
        }
        catch(error){
            console.log(error);
        }
    }, [user])

    const changeImage = (e) => {
        const selectedImage = e.target.files[0];
        const reader = new FileReader();
        console.log(reader);
        reader.readAsDataURL(selectedImage);
        reader.onload = () => {
            setPicture(reader.result);
            console.log(picture);
        };
    }

    const changeAboutMe = (e) => {
        e.preventDefault();
        setAboutMe(e.target.value);
    }

    const editProfile = (e) => {
        e.preventDefault();
        setEdit(true);
    }
    const cancel = (e) => {
        e.preventDefault();
        setAboutMe(user.profile.about_me);
        setPicture(user.profile.profile_picture);
        setEdit(false);
    }

    const saveChanges = (e) => {
        console.log(picture);
        console.log(aboutMe);
        e.preventDefault();
        dispatch(updateProfile(picture, aboutMe)).then(
            r => {
                dispatch(getself());
            }
        );
        setEdit(false);
    }

    return(
        <Box sx={{display: "flex", width: "90%", alignSelf: "center", justifyContent: "center"}}>
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
                        <Button sx={{marginTop: "20px", width: "100%", marginRight: "5px", backgroundColor: "#0c7c59", color: "white", ":hover": {color: "#0c7c59", backgroundColor: "white"}}} onClick={editProfile}>Edit Profile</Button>
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