import React, {useState} from "react";
import {Box, TextField} from "@mui/material";
import Task from "./Task";
const Tasks = ({addTask, tasks, attendees, deleteTask}) => {

    const [input, setInput] = useState("");
    const [attendee, setAttendee] = useState(attendees[0].user.username);

    const [num, setNum] = useState(1);

    console.log(attendees);
    console.log(tasks);
    const handleChange = (e) => {
        e.preventDefault();
        setInput(e.target.value);
    }

    const handleAttendee = (e) => {
        e.preventDefault();
        setAttendee(e.target.value);
    }

    const handleSubmit = (e) => {
        e.preventDefault();
        if(input !== "" && attendee !== ""){
            addTask({n: num, name: attendee, task: {id: attendees.filter((a) => a.user.username === attendee)[0].user.id, task: input}});
            setNum(num+1);
        }
        setInput("");
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
                    <select value={attendee} onChange={handleAttendee} style={{width: '28%', marginRight:"3px"}}>
                        {attendees.map((attendee) => <option>{attendee.user.username}</option>)}
                    </select>
                    <input type="text" value={input} onChange={handleChange} style={{width: "70%"}}/>
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