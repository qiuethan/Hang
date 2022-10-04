import React from "react";
import { useDispatch } from "react-redux";
import { acceptfriendrequest } from "../../../../actions/friends";

const Request = ({user}) => {

    const dispatch = useDispatch();

    const acceptRequest = (e) => {
        e.preventDefault();
        dispatch(acceptfriendrequest(user));
    }

    const declineRequest = () => {

    }

    return(
        <div>
            {user.username}
            <button onClick={acceptRequest}>Accept</button>
            <button onClick={declineRequest}>Decline</button>    
        </div>
    )
}

export default Request;