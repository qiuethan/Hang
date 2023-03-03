import React, { useEffect, useState } from "react";
import { useDispatch, useSelector} from "react-redux";
import {getuser} from "../../../../actions/users";

const Chatitem = ({ roomid, users, type, gcName, setCurrentRoom }) => {

    const dispatch = useDispatch();

    const handleClick = (event) => {
        event.preventDefault();
        setCurrentRoom(roomid);
    }

    const userStorage = useSelector(state => state.users);

    const [name, setName] = useState("");

    console.log(name);

    useEffect(() => {
        if(type === "DM"){
            try{
                const otherUserId = JSON.parse(users).find(user => user !== JSON.parse(localStorage.getItem("profile")).user.id);
                const obj = userStorage.find((user) => user.user.id === otherUserId);
                if(obj === undefined){
                    console.log("Sent to Server");
                    dispatch(getuser(otherUserId));
                }
                else{
                    setName(obj.user.username);
                }
            }
            catch (error){
                setName("Could Not Access User");
            }
        }
        if(type === "GC"){
            setName(gcName);
        }
    }, [useSelector(state => state.users)]);

    return(
        <div>
            <button onClick={handleClick}>{name}</button>
        </div>
    );
};

export default Chatitem;