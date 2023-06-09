import React, { useState } from "react";
import { useDispatch } from "react-redux";
import {loadsentfriendrequests, sendfriendrequest} from "../../../actions/friends";
import {Box, TextField} from "@mui/material";

const Request = () => {

    const [email, setEmail] = useState("");

    const dispatch = useDispatch();

    const handleChange = (event) => {
        event.preventDefault();
        setEmail(event.target.value);
    }

    const handleSubmit = (event) => {
        event.preventDefault();
        dispatch(sendfriendrequest(email)).then((r) => {
            dispatch(loadsentfriendrequests());
            setEmail("");
        });
    }

    return(
        <form onSubmit={handleSubmit} style={{width: "100%", height: "100%", display: "flex", flexDirection: "row", marginLeft: "10px", marginRight: "10px"}}>
            <Box sx={{display: "flex", alignItems:"center", justifyContent: "center", width: "30%", marginRight: "10px", bgcolor: "#a5d6b0", borderRadius: "10px"}}>
                <label htmlFor="email" style={{fontSize: "16px"}}>Send Friend Request: </label>
            </Box>
            <Box sx={{width: "70%"}}>
                <TextField
                    type="text"
                    name="email"
                    value={email || ""}
                    onChange = {handleChange}
                    sx={{width: "100%", "& .MuiOutlinedInput-root":{"& > fieldset": {borderColor: "black"}, '&.Mui-focused .MuiOutlinedInput-notchedOutline': {borderColor: '#0c7c59'}}}}
                    autoComplete="off"
                />
            </Box>
        </form>
    )
}

export default Request;