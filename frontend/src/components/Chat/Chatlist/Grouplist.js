import React, { useEffect } from "react";
import { useDispatch, useSelector } from "react-redux";
import { loadgroups } from "../../../actions/chat";
import Chatitem from "./Chatitem/Chatitem";

const Grouplist = ({ currentRoom, setCurrentRoom, clientOpened }) => {
    
    const dispatch = useDispatch();

    const rooms = useSelector(state => state.groups);

    useEffect(() => {
        if(clientOpened){ 
            dispatch(loadgroups());
            console.log(currentRoom);
        }
    }, [currentRoom, clientOpened]);

    console.log(rooms);
    console.log(currentRoom);

    return(
        (rooms.length === 0) ?  <div/>: <div>
            {rooms.map((room) => 
                <Chatitem roomid = {room.id} users = {JSON.stringify(room.users)} type = {room.channel_type} setCurrentRoom = {setCurrentRoom} gcName={room.name}/>
            )}
        </div>
    );
}

export default Grouplist;