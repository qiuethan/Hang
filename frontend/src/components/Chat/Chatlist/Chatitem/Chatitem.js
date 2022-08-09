import React, { useEffect, useState } from "react";

const Chatitem = ({ roomid, users, type, gcName, setCurrentRoom }) => {
    
    const handleClick = (event) => {
        event.preventDefault();
        setCurrentRoom(roomid);
    }

    const [name, setName] = useState("");

    useEffect(() => {
        if(type === "DM"){
            setName(JSON.parse(users).find(user => user.id !== JSON.parse(localStorage.getItem("profile")).user.id).username);
        }
        if(type === "GC"){
            setName(gcName);
        }
    });

    return(
        <div>
            <button onClick={handleClick}>{name}</button>
        </div>
    );
};

export default Chatitem;