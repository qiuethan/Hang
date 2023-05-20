import React, { useEffect, useState } from "react";
import { useSelector } from "react-redux";
import Friend from "./Friend/Friend";
import {Box} from "@mui/material";

const Friendlist = () => {

    const friends = useSelector(state => state.friends);

    console.log(friends);

    return(
        friends.length === 0 ? <Box/> :
            <Box sx={{display: "flex", flexDirection:"column", width: "99%", height: "98%", overflowY: "scroll"}}>
                {friends.map((friend) => (
                    <Friend key={friend} friend={friend}/>
                ))}
            </Box>
    );
}

export default Friendlist;