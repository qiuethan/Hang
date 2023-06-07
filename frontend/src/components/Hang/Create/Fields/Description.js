/*
Author: Ethan Qiu
Filename: Description.js
Last Modified: June 7, 2023
Description: Allows user to see + edit description
*/

import React from "react";
import { Box, TextField } from "@mui/material";

//Description component
const Description = ({value, handleChange}) => {

    //Render component
    return (
        <Box>
            <Box sx={{display: "flex", width: "100%" ,justifyContent: "center"}}>
                <h3>Description</h3>
            </Box>
            <TextField sx={{width: "100%", input: {color: "white"},"& .MuiOutlinedInput-root":{"&.Mui-focused fieldset": {borderColor: "#0c7c59"},"& > fieldset": {border: {color: "#0c7c59"}}}}}
                multiline
                rows={15}
                wrap="wrap"
                type="text"
                name="description"
                value={value || ""}
                onChange={handleChange}
            />
        </Box>
    )
}

export default Description;