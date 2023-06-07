import React, {useEffect, useState} from "react";
import {useDispatch} from "react-redux";
import {getgooglecalendar, syncgooglecalendar} from "../../../actions/calendar";
import Google from "./Google/Google";
import {Box, Button} from "@mui/material";
import UserCalendar from "./UserCalendar/UserCalendar";

const Calendar = () => {

    const dispatch = useDispatch();

    const [connected, setConnected] = useState(null);

    const [calendars, setCalendars] = useState("");
    const [syncedCalendars, setSynchedCalendars] = useState([]);

    useEffect(() => {
        console.log(syncedCalendars);
    }, [syncedCalendars])

    useEffect(() => {
        dispatch(getgooglecalendar()).then(r => {
           if(r === "Access token not found for the current user."){
               setConnected(false);
           }
           else{
               setConnected(true);
               setCalendars(r);
               setSynchedCalendars(r.filter((calendar) => calendar.previous)
                   .map((calendar) => ({
                       id: calendar.google_calendar_id,
                       name: calendar.name
                   }))
               );
           }
        });
    }, [])

    const update = () => {
        dispatch(syncgooglecalendar(syncedCalendars)).then(r => {
            dispatch(getgooglecalendar()).then(r => {
                if(r === "Access token not found for the current user."){
                    setConnected(false);
                }
                else{
                    setConnected(true);
                    setCalendars(r);
                    setSynchedCalendars(r.filter((calendar) => calendar.previous)
                        .map((calendar) => ({
                            id: calendar.google_calendar_id,
                            name: calendar.name
                        }))
                    );
                }
            });
        });
    }

    return(
        <Box sx={{display: "flex", width: "100%", height: "100%"}}>
            {
                connected === false && (
                    <Google/>
                )
            }
            {
                connected === true && calendars !== "" && (
                    <Box sx={{display: "flex", flexDirection: "column", width: "100%", height: "100%"}}>
                        <Box sx={{display: "flex", flexDirection: "row", width: "100%", height: "10%", marginBottom: "20px"}}>
                            <Box sx={{width: "50%"}}>
                                <h3 style={{margin: 0}}>Sync Calendars</h3>
                            </Box>
                            <Box sx={{display: "flex", width: "50%", justifyContent: "flex-end", alignItems: "center"}}>
                                <Button disableRipple  onClick={update} sx={{backgroundColor: "#0c7c59", color: "white", ":hover": {color: "#0c7c59", backgroundColor: "white"}}}>Save Changes</Button>
                            </Box>
                        </Box>
                        <Box sx={{display: "flex", flexDirection: "column", alignItems: "center", height: "100%", width: "100%", overflowY: "scroll"}}>
                            {calendars.map((calendar) =>
                                <UserCalendar calendar={calendar} synchedCalendars={syncedCalendars} setSynchedCalendars={setSynchedCalendars}/>
                            )}
                        </Box>
                    </Box>
                )
            }
        </Box>
    )
}

export default Calendar;