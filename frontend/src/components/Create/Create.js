import React, { useEffect } from 'react';
import { useState } from 'react';
import Description from './Fields/Description';

import Name from './Fields/Name';

const Create = () => {
    
    const [fields, setFields] = useState({name: "", description: "", picture: "", scheduled_time_start: "", scheduled_time_end: "", latitude: "", longitude: "", budget: 0.00, attendees: [], needs: [], tasks: []});
    const [user, setUser] = useState(JSON.parse(localStorage.getItem("profile")));

    useEffect(() => {
        setFields({...fields, name: `${user.user.username}'s Hang`, description: `A Hang hosted by ${user.user.username}!`});
    }, []);

    const handleChange = (event) => {
        event.preventDefault();
        setFields({...fields, [event.target.name]: event.target.value})
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
        </div>
    )
}

export default Create;