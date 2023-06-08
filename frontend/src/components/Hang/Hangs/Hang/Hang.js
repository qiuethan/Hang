/*
Author: Ethan Qiu
Filename: Hang.js
Last Modified: June 7, 2023
Description: Display details of Hang in short form
*/

import React, {useEffect, useState} from 'react';

import User from "./User";

import {Box, Button} from "@mui/material";
import {useNavigate} from "react-router-dom";
import Location from "./Location";

//Hang component
const Hang = ({hang, setCurrentHang}) => {

    //Define navigation variable
    const navigate = useNavigate();

    //When hang clicked
    const openHang = (e) => {
        e.preventDefault();
        //Set current id
        setCurrentHang(hang.id);
        //Go to room link
        navigate(`/hang?room=${hang.id}`)
    }

    //Define begin and end state variables
    const [begin, setBegin] = useState("");
    const [end, setEnd] = useState("");

    //On render
    useEffect(() => {
        //Set begin and end state variables to hang start and end
        setBegin(new Date(hang.scheduled_time_start));
        setEnd(new Date(hang.scheduled_time_end));
    }, [])

    //Render components
    return(
        <Button onClick={openHang} disableRipple sx={{width: "100%", height: "100%", borderRadius:"15px", color: "black", ":hover": {backgroundColor: "#0c7c59"}}}>
            <Box sx={{width: "100%", height: "99%", backgroundColor:"#a5d6b0", borderRadius: "10px"}}>
                <Box sx={{display: "flex", width: "100%", height: "100%", justifyItems:"center"}}>
                    <Box sx={{display: "flex", flexDirection: "column", justifyContent:"center", alignItems:"center"}}>
                        <Box sx={{display: "flex", height: "50%", width:"95%", flexDirection:"row", justifyContent:"center", alignItems: "center"}}>
                            <Box sx={{display: "flex", width: "30%"}}>
                                <img src={hang.picture} style={{width:"100%", aspectRatio: "1", borderRadius:"5px"}}/>
                            </Box>
                            <Box sx={{display: "flex", width: "70%", flexDirection: "column", alignItems:"center"}}>
                                <Box sx={{display: "block", width: "90%"}}>
                                    <h3 style={{marginBottom: "5px", padding: "10px", backgroundColor:"white", borderRadius: "5px"}}>
                                        {hang.name.length <= 22 && (
                                            hang.name
                                        )}
                                        {hang.name.length > 22 && (
                                            hang.name.substring(0, 22) + "..."
                                        )}
                                    </h3>
                                </Box>
                                <Box sx={{display: "block", width: "100%"}}>
                                    <p>
                                        {hang.description.length <= 25 && (
                                            hang.description
                                        )}
                                        {hang.description.length > 25 && (
                                            hang.description.substring(0, 25) + "..."
                                        )}
                                    </p>
                                </Box>
                            </Box>
                        </Box>
                        <Box sx={{display: "flex", height: "50%", width:"95%", flexDirection:"row"}}>
                            <Box sx={{display: "flex", width: "25%", flexDirection: "column", height: "calc(100% -5px)", overflowY: "auto", justifyContent: "left", alignItems: "center", marginTop: "5px"}}>
                                {hang.attendees.map((attendee) => (
                                    <User attendee={attendee}/>
                                ))}
                            </Box>
                            {begin !== "" && end !== "" && (
                                <Box sx={{display: "flex", width: "25%", flexDirection: "column", height: "calc(100% - 5px)", overflowY: "auto", justifyContent: "left", alignItems: "center", marginTop: "5px"}}>
                                    <Box>{begin.toLocaleString()}</Box>
                                    <Box>To</Box>
                                    <Box>{end.toLocaleString()}</Box>
                                </Box>
                            )}
                            <Box sx={{display: "flex", width: "50%", flexDirection: "column", height: "100%", overflowY: "auto"}}>
                                <Location details={hang}/>
                            </Box>
                        </Box>
                    </Box>
                </Box>
            </Box>
        </Button>
    );

}

export default Hang;