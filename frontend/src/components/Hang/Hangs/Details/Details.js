/*
Author: Ethan Qiu
Filename: Details.js
Last Modified: June 7, 2023
Description: Display details of Hang
*/

import React, {useEffect, useState} from "react";
import {Box, Button} from "@mui/material";
import {useDispatch, useSelector} from "react-redux";
import Heading from "./Fields/Heading";
import Attendee from "./Fields/Attendee";
import {generatejoinlink} from "../../../../actions/hang";
import {FRONTENDURL} from "../../../../constants/actionTypes";
import Location from "./Fields/Location";
import Time from "./Fields/Time";

//Details component
const Details = ({currentHang}) => {

    //Define dispatch
    const dispatch = useDispatch();

    //Get hangs from react store
    const allHangs = useSelector(state => state.hangs);

    //Define details state variable
    const [details, setDetails] = useState("");

    //On render
    useEffect(() => {
        //Set details to room details
        setDetails(allHangs.filter(hang => hang.id === currentHang)[0]);
    }, []);

    //When button clicked
    const copyLink = () => {
        //Generate join link
        dispatch(generatejoinlink(details.id)).then((r) => {
            //Copy link to clicboard
            navigator.clipboard.writeText(`${FRONTENDURL}hang/join?code=${r.invitation_code}`).then(r => {
                alert("Link copied to clipboard")
            });
        });
    }

    //Render components
    return(
        <Box sx={{display: "flex", width: "100%", height: "100%", justifyContent: "center", alignItems: "center"}}>
            {
                details !== "" && (
                    <Box sx={{display: "flex", width: "98%", height: "96%"}}>
                        <Box sx={{display: "block", width: "77%", overflowY: "scroll", marginRight: "10px"}}>
                            <Heading details={details}/>
                            <Box sx={{display: "flex", width: "100%"}}>
                                <Box sx={{display: "flex", width: "50%"}}>
                                    <Time details={details}/>
                                </Box>
                                <Box sx={{display: "flex", width: "50%"}}>
                                    <Location details={details}/>
                                </Box>
                            </Box>
                        </Box>
                        <Box sx={{display: "flex", flexDirection: "column", width: "23%", overflowY: "scroll"}}>
                            {JSON.parse(localStorage.getItem(("profile"))).user.id === details.owner &&
                                (
                                    <Box sx={{display: "flex", flexDirection: "column", width: "100%", height: "9.3%", marginBottom: "5px"}}>
                                        <Button disableRipple sx={{width: "100%", height: "100%", borderRadius: "10px", color: "black", bgcolor: "#a5d6b0", "&:hover": {backgroundColor: "#0c7c59", color: "white"}}} onClick={copyLink}>
                                            Copy Invitation Link
                                        </Button>
                                    </Box>
                                )
                            }
                            <Box sx={{display: "block", flexDirection: "column", width: "100%", height: "90.7%", overflowY: "scroll"}}>
                                {details.attendees.map((attendee) => (
                                    <Attendee attendee={attendee}/>
                                ))}
                            </Box>
                        </Box>
                    </Box>

                )
            }
        </Box>
    )
}

export default Details;