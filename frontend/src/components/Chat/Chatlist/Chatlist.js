import React, { useEffect } from "react";
import { useDispatch, useSelector } from "react-redux";
import { loadrooms } from "../../../actions/chat";
import Chatitem from "./Chatitem/Chatitem";

const Chatlist = ({ currentRoom, setCurrentRoom }) => {
    
    const dispatch = useDispatch();

    useEffect(() => {
        dispatch(loadrooms());
        console.log(currentRoom);
    }, [currentRoom]);

    const rooms = useSelector(state => state.chat);

    console.log(rooms);

    return(
        (rooms.length === 0) ?  <div/>: <div>
            {rooms.map((room) => 
                <Chatitem room = {room.id} setCurrentRoom = {setCurrentRoom}/>
            )}
        </div>
    );
}

export default Chatlist;