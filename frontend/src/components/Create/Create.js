import React, { useEffect } from 'react';
import { useState } from 'react';

const Create = () => {
    
    const [fields, setFields] = useState({name: "", description: "", picture: "", scheduled_time: "", longitude: "", latitude: "", budget: 0.00, attendees: [], needs: [], tasks: []});
    const [user, setUser] = JSON.parse(localStorage.getItem("profile"));

    useEffect(() => {
        setFields({...fields, name: `${user.user.username}'s Hang`});
        
    }, []);

    return(
        <div></div>
    )
}

export default Create;