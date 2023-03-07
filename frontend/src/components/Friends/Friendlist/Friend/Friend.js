import React, {useState, useEffect} from "react";
import {useDispatch, useSelector} from "react-redux";
import { blockfriend, removefriend } from "../../../../actions/friends";
import {getuser} from "../../../../actions/users";

const Friend = ({friend}) => {

    const dispatch = useDispatch();

    console.log(friend);

    const [user, setUser] = useState("");

    const users = useSelector(state => state.users);

    useEffect(() => {
        const obj = users.find((user) => user.user.id === friend)
        if(obj === undefined){
            console.log("Sent to Server");
            dispatch(getuser(friend));
        }
        else{
            setUser(obj.user.username);
        }
    }, [useSelector((state) => state.users)])

    const remove = (e) => {
        e.preventDefault();
        dispatch(removefriend(friend));
    }

    const block = (e) => {
        e.preventDefault();
        dispatch(blockfriend(friend));
    }

    return(
        <div>
            {user}
            <button onClick={remove}>Remove Friend</button>
            <button onClick={block}>Block</button>
        </div>
    );
}

export default Friend;