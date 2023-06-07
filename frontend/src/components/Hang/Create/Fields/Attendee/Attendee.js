/*
Author: Ethan Qiu
Filename: Attendee.js
Last Modified: June 7, 2023
Description: Shows user added attendees
*/

import React from 'react';

//Attendee component
const Attendee = ({attendee}) => {

    //Render component
    return(
        <div>
            {attendee.user.username}
        </div>
    );
}

export default Attendee;