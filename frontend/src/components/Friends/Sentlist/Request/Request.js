import React, {useEffect, useState} from "react";
import { useDispatch } from "react-redux";
import { getuser } from "../../../../actions/users";
import {deletesentfriendrequest} from "../../../../actions/friends";
import {Avatar, Box, Button} from "@mui/material";

const Request = ({user}) => {

    const [userObj, setUserObj] = useState({user: {username: ""} });

    console.log(user);

    const dispatch = useDispatch();

    useEffect(() => {

        const fetchUser = async() => {
            const obj = await dispatch(getuser(user));
            console.log(obj);
            setUserObj(obj)
            console.log(userObj);
        };

        fetchUser().catch((error) => console.log(error));

    }, [])

    console.log(userObj);


    const deleterequest = (e) => {
        e.preventDefault();
        dispatch(deletesentfriendrequest(userObj.user.id));
    }

    return(
        <Box sx={{display: "flex", width: "99.5%", height: "65px", alignItems: "center", marginTop: "5px", borderTop: '0.5px solid black'}}>
            <Box sx={{display: "flex", width: "100%", height: "60px", alignItems: "center", ":hover": {bgcolor: "#a5d6b0"}, borderRadius: "10px", marginTop: "5px"}}>
                <Box sx={{display: "flex", width: "50%", height: "90%", alignItems: "center", marginLeft: "10px"}}>
                    <Avatar src={userObj.profile_picture} sx={{height: "40px", width: "40px"}}/>
                    <h3 style={{margin: "0", fontSize: "20px", marginLeft: "10px"}}>{userObj !== "" && (userObj.user.username)}</h3>
                </Box>
                <Box sx={{display: "flex", width: "50%", height: "100%", alignItems: "center", justifyContent: "flex-end", marginRight: "10px"}}>
                    <Button onClick={deleterequest} sx={{backgroundColor: 'transparent', color: "red",':hover': {backgroundColor: 'transparent'}}}>Delete</Button>
                </Box>
            </Box>
        </Box>
    )
}

export default Request;