/*
Author: Ethan Qiu
Filename: Form.js
Last Modified: June 7, 2023
Description: Allows the user to add attendees
*/

import React, {useState} from 'react';
import { useDispatch } from 'react-redux';
import {getuserbyusername} from "../../../../../actions/users";
import {Box} from "@mui/material";

//Form component
const Form = ({updateAttendee, attendees, fields}) => {

    //Create username state variable
    const [username, setUsername] = useState("");

    //Define dispatch
    const dispatch = useDispatch();

    //Handle update in field
    const updateField = (event) => {
        event.preventDefault();
        setUsername(event.target.value);
    }

    //When form submitted
    const addAttendee = (event) => {
        event.preventDefault();
        //Get user by username and return response
        dispatch(getuserbyusername(username)).then((response) => {
            try{
                //If response found, then check react store to find user
                if(response !== undefined){
                    if(!attendees.map(attendee => attendee.user.id).includes(response.user.id)){
                        //Update attendee variable
                        updateAttendee(response);
                    }
                    //Set username to blank
                    setUsername("");
                }
            }
            catch (error){
                console.log(error);
            }
        })
    }

    //Render component
    return(
        <Box sx={{width: "100%"}}>
            <form onSubmit={addAttendee}>
                <input type="text" value={username} onChange={updateField} style={{width: "100%"}}/>
            </form>
        </Box>
    );
}

export default Form;