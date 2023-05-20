import React, {useEffect, useState} from 'react';
import moment from 'moment';
import {useDispatch, useSelector} from "react-redux";
import {getuser} from "../../../../../actions/users";
import {Box} from "@mui/material";

import SettingsIcon from '@mui/icons-material/Settings';

const Message = ({ message }) => {

    const users = useSelector((state) => state.users);
    const dispatch = useDispatch();
    console.log(users);

    console.log(message);

    const [user, setUser] = useState({});

    console.log(useSelector((state) => state.users));

    useEffect(() => {
        if(message.type === "user_message"){
            const obj = users.find((user) => user.user.id === message.user)
            console.log(users);
            console.log(message.user);
            console.log(obj)
            if(obj === undefined){
                console.log("Sent to Server");
                dispatch(getuser(message.user));
            }
            else{
                setUser(obj);
            }
        }
    }, [useSelector((state) => state.users)])
    console.log(user);

    try{
        return(
            <Box sx={{width: "100%", display: "flex", flexDirection: "row", marginBottom: "5px", marginTop: "5px"}}>
                <Box sx={{width: "47px", marginLeft: "10px"}}>
                    {message.type === "user_message" && (
                        <img src={user.profile_picture} style={{maxWidth: "100%", maxHeight: "100%", objectFit: "cover", aspectRatio: "1", borderRadius: "50%"}}/>
                    )}
                    {message.type !== "user_message" && (
                        <SettingsIcon size="large" sx={{width: "100%"}}/>
                    )}
                </Box>
                <Box sx={{display: "block", maxWidth: "calc(100%-67px)", marginLeft: "10px"}}>
                    {message.type === "user_message" && (
                        <Box sx={{}}>
                            <b><span style={{margin: "0", whiteSpace: "pre-line"}}>{user.user.username}</span></b>
                        </Box>
                    )}
                    <Box sx={{display: "block", width: `1030px`, overflowWrap:"break-word"}}>
                        {message.content}
                    </Box>
                </Box>
            </Box>
        )
    }
    catch(error){
        console.log(error);
    }

}

export default Message;