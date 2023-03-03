import React, {useEffect, useState} from 'react';
import moment from 'moment';
import {useDispatch, useSelector} from "react-redux";
import {getuser} from "../../../../../actions/users";

const Message = ({ message }) => {

    const users = useSelector((state) => state.users);
    const dispatch = useDispatch();
    console.log(users);

    console.log(message);

    const [user, setUser] = useState({});

    console.log(useSelector((state) => state.users));

    useEffect(() => {
        const obj = users.find((user) => user.user.id === message.user)
        console.log(users);
        console.log(message.user);
        console.log(obj)
        if(obj === undefined){
            console.log("Sent to Server");
            dispatch(getuser(message.user));
        }
        else{
            setUser(obj);
        }
    }, [useSelector((state) => state.users)])
    console.log(user);

    try{
        return(
            <div>
                <div>
                    {user.user.username}
                </div>
                <div>
                    {message.content}
                </div>
                <div>
                    {new Date(message.created_at).toLocaleDateString()}
                </div>
            </div>
        )
    }
    catch(error){
        console.log(error);
    }

}

export default Message;