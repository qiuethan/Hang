import React, {useState, useEffect} from "react";
import {useDispatch, useSelector} from "react-redux";
import {getuser} from "../../../../actions/users";
import {unblockeduser} from "../../../../actions/friends";

const Blocked = ({blocked}) => {

    const dispatch = useDispatch();

    console.log(blocked);

    const [user, setUser] = useState("");

    const users = useSelector(state => state.users);

    useEffect(() => {
        const obj = users.find((user) => user.user.id === blocked)
        if(obj === undefined){
            console.log("Sent to Server");
            dispatch(getuser(blocked));
        }
        else{
            setUser(obj.user.username);
        }
    }, [useSelector((state) => state.users)])


    const unblock = () => {
        dispatch(unblockeduser(blocked));
    }

    return(
        <div>
            {user}
            <button onClick={unblock}>Unblock</button>
        </div>
    );
}

export default Blocked;