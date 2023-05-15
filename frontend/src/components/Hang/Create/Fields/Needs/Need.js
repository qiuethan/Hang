import React from "react";
import {Box, Button} from "@mui/material";

const Need = ({need, deleteNeed}) => {

    console.log(need)
    const deleteSelf = (e) => {
        e.preventDefault();
        deleteNeed(need.n);
    }

    return(
        <Box sx={{display: "flex", width: "100%", alignItems:"center"}}>
            <Box sx={{display: "flex", flexGrow: "1", overflowX: "scroll", marginRight: "5px"}}>
                {need.need}
            </Box>
            <Box sx={{display: "flex", justifySelf: "flex-end"}}>
                <Button onClick={deleteSelf} sx={{color: "#0c7c59"}}>Delete</Button>
            </Box>
        </Box>
    )
}

export default Need;