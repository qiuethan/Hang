/*
Author: Ethan Qiu
Filename: Attendees.js
Last Modified: June 7, 2023
Description: Allows users to see + edit attendees
*/

import React, { useEffect } from 'react';

import Attendee from './Attendee/Attendee.js';
import Form from './Attendee/Form.js';
import {Box} from "@mui/material";

//Attendees component
const Attendees = ({attendees, updateAttendee, fields}) => {

    //Render component
    return(
      <Box sx={{width: "100%", height: "50%"}}>
          <Box sx={{display: "flex", flexDirection:"column",width: "100%", height: "100%"}}>
              <Box sx={{height:"50%", width: "100%"}}>
                  <Box sx={{display: "flex", flexDirection: "row", width: "100%", justifyContent: "center"}}>
                      <h3>Invite Attendees</h3>
                  </Box>
                  <Form updateAttendee={updateAttendee} attendees={attendees} fields={fields}/>
              </Box>
              <Box sx={{display:"flex", flexDirection:"column", height: "50%", width: "100%", overflowY: "auto", marginTop: "20px"}}>
                  <Box sx={{display: "flex", flexDirection: "row", width: "100%", justifyContent: "center"}}>
                      <h4>Attendees</h4>
                  </Box>
                  {attendees.map((attendee) => (
                      <Attendee key={attendee.user.id} attendee={attendee} fields={fields}/>
                  ))}
              </Box>
          </Box>
      </Box>
    );
};

export default Attendees;
