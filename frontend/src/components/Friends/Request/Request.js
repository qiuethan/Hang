import React, { useState } from "react";
import { useDispatch } from "react-redux";
import { sendfriendrequest } from "../../../actions/friends";

const Request = () => {

    const [email, setEmail] = useState("");

    const dispatch = useDispatch();

    const handleChange = (event) => {
        event.preventDefault();
        setEmail(event.target.value);
    }

    const handleSubmit = (event) => {
        event.preventDefault();
        dispatch(sendfriendrequest(email));
        setEmail("");
    }

    return(
        <form onSubmit={handleSubmit}>
            <label for="email">Send Friend Request:</label>
            <input
                type="text"
                name="email"
                value={email || ""}
                onChange = {handleChange}
            />
        </form>
    )
}

export default Request;