import React from 'react';

import Attendee from './Attendee/Attendee.js'

const Attendees = ({Attendees}) => {
    return(
      <div>
          {Attendees.map((attendee) => {
              <Attendee attendee={attendee}/>
          })}
      </div>
    );
};

export default Attendees;
