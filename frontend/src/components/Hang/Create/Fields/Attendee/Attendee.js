import React from 'react';

const Attendee = ({attendee}) => {

    console.log(attendee);

    return(
        <div>
            {attendee.user.username}
        </div>
    );
}

export default Attendee;