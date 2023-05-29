import React, {useEffect, useState} from "react";
import {Box} from "@mui/material";
import Task from "./Task";

const Tasks = ({details}) => {

    const [input, setInput] = useState("");
    const [attendee, setAttendee] = useState("");
    const [tasks, setTasks] = useState([]);

    useEffect(() => {
        setTasks([...details.tasks]);
    }, [])

    const handleSubmit = (e) => {
        e.preventDefault();
    }

    const [num, setNum] = useState(1);

    const deleteTask = (event, id) => {

    }

    const handleChange = () => {

    }

    return(
        <Box sx={{height: "100%", width: "100%", display: "flex", flexDirection: "column"}}>
            <Box sx={{width: "100%", height: "10%"}}>
                <Box sx={{display: "flex", flexDirection: "row", width: "100%", justifyContent: "center"}}>
                    <h3>Add Tasks</h3>
                </Box>
            </Box>
            <Box sx={{width: "100%", height: "10%", display: "flex", flexDirection: "column", alignItems:"center", justifyContent:"center"}}>
                <Box sx={{width: "100%", display: "flex", flexDirection:"row", alignItems:"center"}}></Box>
                <form onSubmit={handleSubmit} style={{width: "100%"}}>
                    <input type="text" value={input} onChange={handleChange} style={{width: "100%"}}/>
                </form>
            </Box>
            <Box sx={{width: "100%", height: "10%"}}>
                <Box sx={{display: "flex", flexDirection: "row", width: "100%", justifyContent: "center"}}>
                    <h4>Tasks</h4>
                </Box>
            </Box>
            <Box sx={{width: "100%", height: "70%", display: "block", overflowY: "scroll"}}>
                {tasks.map((task) => (
                    <Task task={task} deleteTask={deleteTask}/>
                ))}
            </Box>
        </Box>
    )
}

export default Tasks;