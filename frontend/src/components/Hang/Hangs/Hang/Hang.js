import React from 'react';

const Hang = ({props}) => {

    return(
        <div>
            {props.name}
            {props.description}
            {props.picture}
        </div>
    );

}

export default Hang;