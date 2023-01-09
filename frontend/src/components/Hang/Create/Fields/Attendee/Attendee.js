import React from 'react';

const Attendee = ({attendee}) => {

    return(
        <div>
            {attendee.user.username}
        </div>
    );
}

export default Attendee;