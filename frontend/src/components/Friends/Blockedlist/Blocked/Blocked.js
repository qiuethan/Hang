/*
Author: Ethan Qiu
Filename: Blocked.js
Last Modified: June 7, 2023
Description: Displays blocked user
*/

import React, {useState, useEffect} from "react";
import {useDispatch, useSelector} from "react-redux";
import {getuser} from "../../../../actions/users";
import {unblockeduser} from "../../../../actions/friends";
import {Avatar, Box, Button} from "@mui/material";

const Blocked = ({blocked}) => {

    //Define dispatch
    const dispatch = useDispatch();

    //Initialize state variable
    const [user, setUser] = useState("");

    //Get users from react store
    const users = useSelector(state => state.users);

    //On render
    useEffect(() => {
        //Get object from user id
        const obj = users.find((user) => user.user.id === blocked)
        //Not found
        if(obj === undefined){
            //Get user object from API
            dispatch(getuser(blocked));
        }
        else{
            //Set user to object
            setUser(obj);
        }
    }, [useSelector((state) => state.users)])


    //When unblock button pressed
    const unblock = () => {
        //Unblock user
        dispatch(unblockeduser(blocked));
    }

    //Render component
    return(
        <Box sx={{display: "flex", width: "99.5%", height: "65px", alignItems: "center", marginTop: "5px", borderTop: '0.5px solid black'}}>
            <Box sx={{display: "flex", width: "100%", height: "60px", alignItems: "center", ":hover": {bgcolor: "#a5d6b0"}, borderRadius: "10px", marginTop: "5px"}}>
                <Box sx={{display: "flex", width: "50%", height: "90%", alignItems: "center", marginLeft: "10px"}}>
                    <Avatar src={user.profile_picture} sx={{height: "40px", width: "40px"}}/>
                    <h3 style={{margin: "0", fontSize: "20px", marginLeft: "10px"}}>{user !== "" && (user.user.username)}</h3>
                </Box>
                <Box sx={{display: "flex", width: "50%", height: "100%", alignItems: "center", justifyContent: "flex-end", marginRight: "10px"}}>
                    <Button onClick={unblock} sx={{backgroundColor: 'transparent', color: "black",':hover': {backgroundColor: 'transparent'} }}>Unblock</Button>
                    </Box>
            </Box>
        </Box>
    );
}

export default Blocked;