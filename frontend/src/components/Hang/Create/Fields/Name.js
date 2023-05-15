import React from "react";

import {Box, TextField} from "@mui/material";

const Name = ({value, handleChange}) => {
    return (
        <Box sx={{display: "flex", width: "100%", alignItems: "center"}}>
            <TextField autoComplete="off" sx={{width: "100%", fontSize: "24px", borderRadius: "10px", input : {color: "white"}, bgcolor: "#0c7c59", "& .MuiOutlinedInput-root":{"& > fieldset": {border: "none"}}, "& .MuiInputLabel-root":{color: "white"}, "& label.Mui-focused": {color: "white"}}}
                type="text"
                name="name"
                label={value === "" ? "Enter Hang Name" : ""}
                value={value || ""}
                onChange={handleChange}
                InputLabelProps={{shrink: false, style: {fontSize: "24px"}}}
                InputProps={{
                    style:{
                        fontSize: "24px",
                    },
                    form:{
                        autocomplete: 'off',
                    },
                }}
            />
        </Box>
    )
}

export default Name;