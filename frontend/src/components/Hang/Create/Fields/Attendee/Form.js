import React, {useState} from 'react';

const Form = ({updateAttendee}) => {

    const [username, setUsername] = useState("");

    const updateField = (event) => {
        event.preventDefault();
        setUsername(event.target.value);
    }

    const addAttendee = (event) => {
        event.preventDefault();
        
    }

    return(
        <div>
            <form onSubmit={addAttendee}>
                <input type="text" value={username} onChange={updateField}/>
            </form>
        </div>
    );
}

export default Form;