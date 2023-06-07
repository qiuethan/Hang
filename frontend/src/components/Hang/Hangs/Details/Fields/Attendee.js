import React, {useEffect, useState} from "react";
import {Avatar, Box} from "@mui/material";
import {useDispatch, useSelector} from "react-redux";
import {getuser} from "../../../../../actions/users";

const Attendee = ({attendee}) => {

    const dispatch = useDispatch();

    console.log(attendee);

    const [user, setUser] = useState("");

    const users = useSelector(state => state.users);

    console.log(user);

    useEffect(() => {
        const obj = users.find((user) => user.user.id === attendee)
        if(obj === undefined){
            console.log("Sent to Server");
            dispatch(getuser(attendee));
        }
        else{
            setUser(obj);
        }
    }, [useSelector((state) => state.users)])

    return(
        <Box sx={{display: "block", width: "100%", height: "60px", alignItems: "center", justifyContent: "center", ":hover": {bgcolor: "#a5d6b0"}, borderRadius: "10px", marginBottom: "10px"}}>
            {user !== "" && (
                <Box sx={{display: "flex", width: "100%", height: "90%", alignItems: "center", marginLeft: "10px"}}>
                    <Avatar src={user.profile_picture} sx={{height: "40px", width: "40px"}}/>
                    <h3 style={{margin: "0", fontSize: "20px", marginLeft: "10px"}}>{user !== "" && (user.user.username)}</h3>
                </Box>
            )}
        </Box>
    )
}

export default Attendee;