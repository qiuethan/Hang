import React, {useEffect} from 'react';

import User from "./User";

import {Box, Button} from "@mui/material";
import {useNavigate} from "react-router-dom";

const Hang = ({hang, setCurrentHang}) => {

    console.log(hang);

    const navigate = useNavigate();

    const openHang = (e) => {
        e.preventDefault();
        setCurrentHang(hang.id);
        navigate(`/hang?room=${hang.id}`)
    }

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
                        <Box sx={{display: "flex", height: "50%", width:"95%", flexDirection:"row", justifyContent:"center", alignItems: "center"}}>
                            {hang.attendees.map((attendee) => (
                                <User attendee={attendee}/>
                            ))}
                        </Box>
                    </Box>
                </Box>
            </Box>
        </Button>
    );

}

export default Hang;