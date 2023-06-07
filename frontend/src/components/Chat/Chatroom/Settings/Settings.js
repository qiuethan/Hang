/*
Author: Ethan Qiu
Filename: Settings.js
Last Modified: June 7, 2023
Description: Renders settings bar at top of chat + allows access to settings
*/

import React, {useEffect, useState} from "react";
import {Box, Button} from "@mui/material";
import {useDispatch, useSelector} from "react-redux";
import {getuser} from "../../../../actions/users";
import SettingsIcon from "@mui/icons-material/Settings";

// Define the Settings component
const Settings = ({currentRoom, settings, setSettings}) => {

    // Define dispatch method
    const dispatch = useDispatch();

    // Get user details from localstorage
    const user = JSON.parse(localStorage.getItem('profile'));

    // Get all the users from react store
    const allUsers = useSelector(state => state.users);

    // Store other user's details
    const [otherUser, setOtherUser] = useState("");

    // Find room with correct details
    const dmDetails = useSelector(state => state.dms).filter(room => room.id === currentRoom)[0];
    const groupDetails = useSelector(state => state.groups).filter(room => room.id === currentRoom)[0];

    // On render
    useEffect(() => {
        if(dmDetails){
            // Find the other user from the DM who is not the current user.
            const dmUser = allUsers.find(u => u.user.id === dmDetails.users.filter(u => u !== user.user.id)[0]);
            if(!dmUser){
                // if not present in react store, cal API to find
                dispatch(getuser(dmDetails.users.filter(u => u !== user.user.id)[0]));
            }
            else{
                // Set user to found user
                setOtherUser(dmUser);
            }
        }
    }, [useSelector((state) => state.users), currentRoom])

    // Check if button is hovered over
    const [buttonHover, setButtonHover] = useState(false);

    // Handle when settings button is clicked
    const handleSettings = () => {
        setSettings(!settings);
    }

    // Render component
    return(
        <Box sx={{display: "flex", height: "100%", width: "100%", bgcolor:"#0c7c59", alignItems: "center", justifyContent: "center", borderRadius: "10px 10px 0 0"}}>
            {dmDetails && (
                <Box sx={{display: "flex", flexDirection: "row", height: "80%", width: "98%"}}>
                    <Box sx={{display: "flex", width: "50%", height: "100%", alignItems: "center"}}>
                        {otherUser !== "" && (
                            <h3 style={{margin: "0", color: "white"}}>{otherUser.user.username}</h3>
                        )}
                    </Box>
                </Box>
            )}
            {groupDetails && (
                <Box sx={{display: "flex", flexDirection: "row", height: "80%", width: "98%"}}>
                    <Box sx={{display: "flex", width: "50%", height: "100%", alignItems: "center"}}>
                        <h3 style={{margin: "0", color: "white"}}>{groupDetails.name}</h3>
                    </Box>
                    <Box sx={{display: "flex", flexDirection: "row-reverse", alignItems:"center", width: "50%", height: "100%"}}>
                        <Button onClick={handleSettings} disableRipple onMouseEnter={() => setButtonHover(true)} onMouseLeave={() => setButtonHover(false)}><SettingsIcon sx={{color: buttonHover ? "#a5d6b0" : "white"} }/></Button>
                    </Box>
                </Box>
            )}
        </Box>
    )
}

export default Settings;