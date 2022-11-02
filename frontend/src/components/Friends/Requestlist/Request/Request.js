import React from "react";
import { useDispatch } from "react-redux";
import { acceptfriendrequest, declinefriendrequest } from "../../../../actions/friends";

const Request = ({user}) => {

    const dispatch = useDispatch();

    const acceptRequest = (e) => {
        e.preventDefault();
        dispatch(acceptfriendrequest(user));
    }

    const declineRequest = (e) => {
        e.preventDefault();
        dispatch(declinefriendrequest(user));
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