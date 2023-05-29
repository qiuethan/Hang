import React, {useEffect, useState} from "react";
import {Box} from "@mui/material";
import {useSelector} from "react-redux";
import Heading from "./Fields/Heading";
import Tasks from "./Fields/Tasks/Tasks";
import Attendee from "./Fields/Attendee";

const Details = ({currentHang}) => {

    const allHangs = useSelector(state => state.hangs);

    console.log(allHangs.filter(hang => hang.id === currentHang)[0]);

    const [details, setDetails] = useState("");

    useEffect(() => {
        setDetails(allHangs.filter(hang => hang.id === currentHang)[0]);
    }, []);

    return(
        <Box sx={{display: "flex", width: "100%", height: "100%", justifyContent: "center", alignItems: "center"}}>
            {
                details !== "" && (
                    <Box sx={{display: "flex", width: "98%", height: "96%", overflowY: "scroll"}}>
                        <Box sx={{display: "flex", flexDirection: "column", width: "77%"}}>
                            <Heading details={details}/>
                            Hello
                        </Box>
                        <Box sx={{display: "flex", flexDirection: "column", width: "23%", overflowY: "scroll"}}>
                            {details.attendees.map((attendee) => (
                                <Attendee attendee={attendee}/>
                            ))}
                        </Box>
                    </Box>

                )
            }
        </Box>
    )
}

export default Details;