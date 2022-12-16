import React, { useEffect } from 'react';
import { useState } from 'react';
import { useDispatch } from 'react-redux'

import Name from './Fields/Name';
import Description from './Fields/Description';
import Picture from './Fields/Picture';
import Time from './Fields/Time';
import Location from './Fields/Location';
import Attendees from './Fields/Attendees';

import { createhangevent } from '../../../actions/create';

const Create = () => {
    
    const [user, setUser] = useState(JSON.parse(localStorage.getItem("profile")));

    const [fields, setFields] = useState({name: "", owner: user.user.id, description: "", picture: "", scheduled_time_start: "", scheduled_time_end: "", latitude: 0, longitude: 0, budget: 0.00, attendees: [user.user.id], needs: [], tasks: []});

    const dispatch = useDispatch();

    useEffect(() => {
        setFields({...fields, name: `${user.user.username}'s Hang`, description: `A Hang hosted by ${user.user.username}!`});
    }, []);

    const handleChange = (event) => {
        event.preventDefault();
        setFields({...fields, [event.target.name]: event.target.value})
    }

    const handleSubmit = (event) => {
        event.preventDefault();
        console.log(fields);
        dispatch(createhangevent(fields));
    }

    return(
        <div>
            <Name value={fields.name} handleChange={handleChange}/>
            <Description value={fields.description} handleChange={handleChange}/>
            <Picture value={fields.picture} handleChange={handleChange}/>
            <Time start={fields.scheduled_time_start} end={fields.scheduled_time_end} handleChange={handleChange}/>
            <Location longitude={fields.longitude} latitude={fields.latitude} handleChange={handleChange}/>
            <Attendees attendees={fields.attendees}/>
            <button onClick={handleSubmit}>Submit</button>
        </div>
    )
}

export default Create;