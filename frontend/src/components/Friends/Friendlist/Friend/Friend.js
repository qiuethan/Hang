/*
Author: Ethan Qiu
Filename: Friend.js
Last Modified: June 7, 2023
Description: Displays Friend in friendlist
*/

import React, {useState, useEffect} from "react";
import {useDispatch, useSelector} from "react-redux";
import { blockfriend, removefriend } from "../../../../actions/friends";
import {getuser} from "../../../../actions/users";
import {Avatar, Box, Button} from "@mui/material";

//Friend component
const Friend = ({friend}) => {

    //Define dispatch
    const dispatch = useDispatch();

    //Define user state variable
    const [user, setUser] = useState("");

    //Get users from react store
    const users = useSelector(state => state.users);

    //On render
    useEffect(() => {
        //Find user object with id
        const obj = users.find((user) => user.user.id === friend)
        //If not found
        if(obj === undefined){
            //Get object from API
            dispatch(getuser(friend));
        }
        else{
            //Set user to object
            setUser(obj);
        }
    }, [useSelector((state) => state.users)])

    //When button pressed to remove friend
    const remove = (e) => {
        e.preventDefault();
        //Dispatch to backend
        dispatch(removefriend(friend));
    }

    //When button pressed to block friend
    const block = (e) => {
        e.preventDefault();
        //Dispatch to backend
        dispatch(blockfriend(friend));
    }

    //Render Component
    return(
        <Box sx={{display: "flex", width: "99.5%", height: "65px", alignItems: "center", marginTop: "5px", borderTop: '0.5px solid black'}}>
            <Box sx={{display: "flex", width: "100%", height: "60px", alignItems: "center", ":hover": {bgcolor: "#a5d6b0"}, borderRadius: "10px", marginTop: "5px"}}>
                <Box sx={{display: "flex", width: "50%", height: "90%", alignItems: "center", marginLeft: "10px"}}>
                    <Avatar src={user.profile_picture} sx={{height: "40px", width: "40px"}}/>
                    <h3 style={{margin: "0", fontSize: "20px", marginLeft: "10px"}}>{user !== "" && (user.user.username)}</h3>
                </Box>
                <Box sx={{display: "flex", width: "50%", height: "100%", alignItems: "center", justifyContent: "flex-end", marginRight: "10px"}}>
                    <Button onClick={remove} sx={{backgroundColor: 'transparent', color: "black",':hover': {backgroundColor: 'transparent'} }}>Remove Friend</Button>
                    <Button onClick={block} sx={{backgroundColor: 'transparent', color: "red",':hover': {backgroundColor: 'transparent'}}}>Block</Button>
                </Box>
            </Box>
        </Box>
    );
}

export default Friend;