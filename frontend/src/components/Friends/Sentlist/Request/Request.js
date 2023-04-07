import React, {useEffect, useState} from "react";
import { useDispatch } from "react-redux";
import { getuser } from "../../../../actions/users";
import {deletesentfriendrequest} from "../../../../actions/friends";

const Request = ({user}) => {

    const [userObj, setUserObj] = useState({user: {username: ""} });

    console.log(user);

    const dispatch = useDispatch();

    useEffect(() => {

        const fetchUser = async() => {
            const obj = await dispatch(getuser(user));
            console.log(obj);
            setUserObj(obj)
            console.log(userObj);
        };

        fetchUser().catch((error) => console.log(error));

    }, [])

    console.log(userObj);


    const deleterequest = (e) => {
        e.preventDefault();
        dispatch(deletesentfriendrequest(userObj.user.id));
    }

    return(
        <div>
        {(userObj.user.username !== "") && (
            <div>
                {userObj.user.username}
                <button onClick={deleterequest}>Delete</button>
            </div>
        )}
        </div>
    )
}

export default Request;