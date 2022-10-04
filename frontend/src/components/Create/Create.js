import React, { useEffect } from 'react';
import { useState } from 'react';
import { useDispatch } from 'react-redux'

import Name from './Fields/Name';
import Description from './Fields/Description';
import { createhangevent } from '../../actions/create';

const Create = () => {
    
    const [fields, setFields] = useState({name: "", description: "", picture: "", scheduled_time_start: "", scheduled_time_end: "", latitude: "", longitude: "", budget: 0.00, attendees: [], needs: [], tasks: []});
    const [user, setUser] = useState(JSON.parse(localStorage.getItem("profile")));

    const dispatch = useDispatch()

    useEffect(() => {
        setFields({...fields, name: `${user.user.username}'s Hang`, description: `A Hang hosted by ${user.user.username}!`});
    }, []);

    const handleChange = (event) => {
        event.preventDefault();
        setFields({...fields, [event.target.name]: event.target.value})
    }

    const handleSubmit = (event) => {
        event.preventDefault();
        dispatch(createhangevent(fields))
    }

    return(
        <div>
            <Name value={fields.name} handleChange={handleChange}/>
            <Description value = {fields.description} handleChange={handleChange}/>
            <input
                type="text"
                name="picture"
                value={fields.picture || ""}
                onChange={handleChange}
            />
            <input
                type="text"
                name="scheduled_time_start"
                value={fields.scheduled_time_start || ""}
                onChange={handleChange}
            />
            <input
                type="text"
                name="scheduled_time_end"
                value={fields.scheduled_time_end || ""}
                onChange={handleChange}
            />
            <button onClick={handleSubmit}>Submit</button>
        </div>
    )
}

export default Create;