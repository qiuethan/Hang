import React, {useState} from 'react';
import { useDispatch } from 'react-redux';
import {getuserbyusername} from "../../../../../actions/users";
import {Box} from "@mui/material";

const Form = ({updateAttendee, attendees, fields}) => {

    const [username, setUsername] = useState("");
    const dispatch = useDispatch();

    const updateField = (event) => {
        event.preventDefault();
        setUsername(event.target.value);
    }

    console.log(attendees);

    const addAttendee = (event) => {
        event.preventDefault();
        dispatch(getuserbyusername(username)).then((response) => {
            try{
                if(response !== undefined){
                    if(!attendees.map(attendee => attendee.user.id).includes(response.user.id)){
                        updateAttendee(response);

                    }
                    setUsername("");
                }
            }
            catch (error){
                console.log(error);
            }
        })
    }

    return(
        <Box sx={{width: "100%"}}>
            <form onSubmit={addAttendee}>
                <input type="text" value={username} onChange={updateField} style={{width: "100%"}}/>
            </form>
        </Box>
    );
}

export default Form;