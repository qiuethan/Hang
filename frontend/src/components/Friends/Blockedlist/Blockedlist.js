import React, { useEffect, useState } from "react";
import Blocked from "./Blocked/Blocked";
import {useSelector} from "react-redux";
import {Box} from "@mui/material";

const Blockedlist = () => {

    const blocked = useSelector(state => state.blocked);

    console.log(blocked);

    return(
        blocked.length === 0 ? <Box/> : <Box sx={{display: "flex", flexDirection:"column", width: "99%", height: "98%", overflowY: "scroll"}}>
        {blocked.map((blocked) => (
                <Blocked key={blocked} blocked={blocked}/>
            ))}
        </Box>
    );
}

export default Blockedlist;