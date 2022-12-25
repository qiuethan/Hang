import React, {useState} from 'react';
import { useDispatch } from 'react-redux';
import {getuserbyusername} from "../../../../../actions/users";

const Form = ({updateAttendee}) => {

    const [username, setUsername] = useState("");
    const dispatch = useDispatch();

    const updateField = (event) => {
        event.preventDefault();
        setUsername(event.target.value);
    }

    const addAttendee = (event) => {
        event.preventDefault();
        dispatch(getuserbyusername(username)).then((response) => {
            try{
                updateAttendee(response);
            }
            catch (error){
                console.log(error);
            }
        })
        setUsername("");
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