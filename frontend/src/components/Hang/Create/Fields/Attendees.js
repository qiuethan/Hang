import React, { useEffect } from 'react';

import Attendee from './Attendee/Attendee.js';
import Form from './Attendee/Form.js';

const Attendees = ({attendees, updateAttendee}) => {

    console.log(attendees);

    useEffect(()=>{

    }, [attendees]);

    return(
      <div>
          <Form updateAttendee={updateAttendee}/>
          {attendees.map((attendee) => (
              <Attendee key={attendee.id} attendee={attendee}/>
          ))}
      </div>
    );
};

export default Attendees;
