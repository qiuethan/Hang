import React from "react";

const Chatitem = ({ room, setCurrentRoom }) => {
    
    const handleClick = (event) => {
        event.preventDefault();
        setCurrentRoom(room);
    }

    return(
        <div>
            <button onClick={handleClick}>{room}</button>
        </div>
    );
};

export default Chatitem;