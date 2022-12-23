import React from 'react';

const Attendee = ({attendee}) => {

    console.log(attendee);

    return(
        <div>
            {attendee.username}
        </div>
    );
}

export default Attendee;