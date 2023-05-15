import React, {useState} from "react";
import {Box, TextField} from "@mui/material";

import Need from "./Need";
const Needs = ({addNeed, needs, deleteNeed}) => {

    const [input, setInput] = useState("");

    const [num, setNum] = useState(1);

    const handleChange = (e) => {
        e.preventDefault();
        setInput(e.target.value);
    }

    const handleSubmit = (e) => {
        e.preventDefault();
        if(input !== ""){
            addNeed({n: num, need: input});
            setNum(num+1);
        }
        setInput("");
    }

    return(
        <Box sx={{height: "100%", width: "100%", display: "flex", flexDirection: "column"}}>
            <Box sx={{width: "100%", height: "10%"}}>
                <Box sx={{display: "flex", flexDirection: "row", width: "100%", justifyContent: "center"}}>
                    <h3>Add Needs</h3>
                </Box>
            </Box>
            <Box sx={{width: "100%", height: "10%", display: "flex", flexDirection: "column", alignItems:"center", justifyContent:"center"}}>
                <form onSubmit={handleSubmit} style={{width: "100%"}}>
                    <input type="text" value={input} onChange={handleChange} style={{width: "100%"}}/>
                </form>
            </Box>
            <Box sx={{width: "100%", height: "10%"}}>
                <Box sx={{display: "flex", flexDirection: "row", width: "100%", justifyContent: "center"}}>
                    <h4>Needs</h4>
                </Box>
            </Box>
            <Box sx={{width: "100%", height: "70%", display: "block", overflowY: "scroll"}}>
               {needs.map((need) => (
                    <Need need={need} deleteNeed={deleteNeed}/>
                ))}
            </Box>
        </Box>
    )
}

export default Needs;