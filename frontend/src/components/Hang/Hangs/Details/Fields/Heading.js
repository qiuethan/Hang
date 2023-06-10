/*
Author: Ethan Qiu
Filename: Details.js
Last Modified: June 7, 2023
Description: Display name, description, picture of Hang
*/

import React from "react";
import {Box} from "@mui/material";

//Heading component
const Heading = ({details}) => {

    //Render components
    return(
        <Box sx={{display: "flex", flexDirection: "row", width: "100%", marginBottom: "20px"}}>
            <Box sx={{width: "20%"}}>
                <img style={{display: "block", justifySelf: "center", alignSelf: "center", maxWidth: "100%", maxHeight: "100%", aspectRatio:"1", objectFit: "cover", borderRadius: "50%"}} src={details.picture} alt="Picture"/>
            </Box>
            <Box sx={{display: "flex", flexDirection: "column", width: "80%", marginLeft: "15px"}}>
                <Box sx={{bgcolor: "#a5d6b0", borderRadius: "10px", overflowX: "auto"}}>
                    <h2 style={{marginLeft: "10px", marginTop: "10px", marginBottom: "10px"}}>{details.name}</h2>
                </Box>
                <Box>
                    <p style={{marginLeft: "10px"}}>{details.description}</p>
                </Box>
            </Box>
        </Box>
    )
}

export default Heading;