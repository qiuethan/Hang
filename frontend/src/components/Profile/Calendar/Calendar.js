/*
Author: Ethan Qiu
Filename: Calendar.js
Last Modified: June 7, 2023
Description: Allow users to connect + display + sync calendars
*/

import React, {useEffect, useState} from "react";
import {useDispatch} from "react-redux";
import {getgooglecalendar, syncgooglecalendar} from "../../../actions/calendar";
import Google from "./Google/Google";
import {Box, Button} from "@mui/material";
import UserCalendar from "./UserCalendar/UserCalendar";

//Calendar component
const Calendar = () => {

    //Define dispatch variable
    const dispatch = useDispatch();

    //Define connected state variable
    const [connected, setConnected] = useState(null);

    //Define calendars state variable
    const [calendars, setCalendars] = useState("");

    //Define synced calendars state variable
    const [syncedCalendars, setSynchedCalendars] = useState([]);

    //On render + synced calendar change
    useEffect(() => {
        //Update state variable
        console.log(syncedCalendars);
    }, [syncedCalendars])

    //On Render
    useEffect(() => {
        //Get google calendars
        dispatch(getgooglecalendar()).then(r => {
           //Not found, not connected to google calendar
           if(r === "Access token not found for the current user."){
               setConnected(false);
           }
           else{
               //Found, connect to google calendar
               setConnected(true);
               //Set calendars to calendars from API
               setCalendars(r);
               //Map previously synced calendars to synchedcalendars
               setSynchedCalendars(r.filter((calendar) => calendar.previous)
                   .map((calendar) => ({
                       id: calendar.google_calendar_id,
                       name: calendar.name
                   }))
               );
           }
        });
    }, [])

    //Update sync when user presses save changes
    const update = () => {
        //Send request to API
        dispatch(syncgooglecalendar(syncedCalendars)).then(r => {
            //Get new google calendars
            dispatch(getgooglecalendar()).then(r => {
                //If access denied
                if(r === "Access token not found for the current user."){
                    setConnected(false);
                }
                else{
                    //Set new calendars to updated values
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

    //Render components
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