import React, {useEffect, useState} from "react";
import {Box} from "@mui/material";
import {useDispatch, useSelector} from "react-redux";
import {getuser} from "../../../../actions/users";

const User = ({attendee}) => {

    const dispatch = useDispatch();

    const [friend, setFriend] = useState("");
    const users = useSelector(state => state.users);

    useEffect(() => {
        const obj = users.find((user) => user.user.id === attendee)
        if(obj === undefined){
            console.log("Sent to Server");
            dispatch(getuser(attendee));
        }
        else{
            setFriend(obj.user.username);
        }
    }, [useSelector((state) => state.users)])

    return(
        <Box>
            {friend !== "" && (
                friend
            )}
        </Box>
    )
}

export default User;