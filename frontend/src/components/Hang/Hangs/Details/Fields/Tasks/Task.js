import React from "react";
import {Box, Button} from "@mui/material";

const Task = ({task, deleteTask}) => {

    const deleteSelf = (e) => {
        e.preventDefault();
        deleteTask(task.event, task.id);
    }

    return(
        <Box sx={{display: "flex", width: "100%", alignItems:"center"}}>
            <Box sx={{display: "flex", marginRight: "5px", width:"85%"}}>
                {task.name}
            </Box>
            <Box sx={{display: "flex", justifySelf: "flex-end"}}>
                <Button onClick={deleteSelf} sx={{color: "#0c7c59"}}>Delete</Button>
            </Box>
        </Box>
    )
}

export default Task;