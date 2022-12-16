import React from 'react';

import Attendee from './Attendee/Attendee.js'

const Attendees = ({attendees}) => {

    return(
      <div>
          {attendees.map((attendee) => {
              <Attendee attendee={attendee}/>
          })}
      </div>
    );
};

export default Attendees;
