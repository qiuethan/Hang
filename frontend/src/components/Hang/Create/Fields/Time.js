/*
Author: Ethan Qiu
Filename: Time.js
Last Modified: June 7, 2023
Description: Allows user to see + edit time
*/

import React from "react";
import { Box } from "@mui/material";

//Time component
const Time = ({start, end, handleChange}) => {

    //Render component
    return(
        <Box sx={{display:"flex", flexDirection:"column", height: "100%", width:"100%", marginRight: "10px", overflowY: "auto"}}>
            <Box sx={{height: "50%", width: "100%"}}>
                <Box sx={{display: "flex", flexDirection: "row", width: "100%", justifyContent: "center"}}>
                    <h3>Start Time</h3>
                </Box>
                <input
                    type="datetime-local"
                    name="scheduled_time_start"
                    value={start || ""}
                    onChange={handleChange}
                    style={{width:"100%"}}
                />
            </Box>
            <Box sx={{height: "50%", width: " 100%"}}>
                <Box sx={{display: "flex", flexDirection: "row", width: "100%", justifyContent: "center"}}>
                    <h3>End Time</h3>
                </Box>
                <input
                    type="datetime-local"
                    name="scheduled_time_end"
                    value={end || ""}
                    onChange={handleChange}
                    style={{width:"100%"}}
                />
                {end < start && (
                    <Box sx={{display: "flex", width: "100%", justifyContent: "center"}}>
                        <p style={{margin: "0", marginTop: "3px", color: "red"}}>End date + time must be after start date + time!</p>
                    </Box>
                )}
            </Box>
        </Box>
    )
}

export default Time