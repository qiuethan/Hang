/*
Author: Ethan Qiu
Filename: Time.js
Last Modified: June 7, 2023
Description: Display time of Hang
*/

import React, {useEffect, useState} from "react";
import {Box} from "@mui/material";

//Time Component
const Time = ({details}) => {

    //Create begin and end state variables
    const [begin, setBegin] = useState("");
    const [end, setEnd] = useState("");

    //On render
    useEffect(() => {
        //Set begin and end states to hang begin and end
        setBegin(new Date(details.scheduled_time_start));
        setEnd(new Date(details.scheduled_time_end));
    }, [])

    //Render components
    return(
        <Box sx={{display: "flex", width: "100%", height: "390px", bgcolor: "#a5d6b0", borderRadius: "10px", marginRight: "5px"}}>
            {begin !== "" && end !== "" && (
                <Box sx={{display: "flex", flexDirection: "column", width: "100%", margin: "10px", alignItems: "center"}}>
                    <Box sx={{display: "flex", flexDirection: "row", width: "100%"}}>
                        <Box sx={{display: "flex", width: "50%", alignItems: "center", justifyContent: "center"}}>
                            <h3 style={{margin: "0", fontSize: "16px"}}>Starts: {begin.toLocaleString()}</h3>
                        </Box>
                        <Box sx={{display: "flex", width: "50%", alignItems: "center", justifyContent: "center"}}>
                            <h3 style={{margin: "0", fontSize: "16px"}}>Ends: {end.toLocaleString()}</h3>
                        </Box>
                    </Box>
                    <Box sx={{marginTop: '10px'}}>
                        Budget: ${details.budget}
                    </Box>
                </Box>
            )}
        </Box>
    )
}

export default Time;