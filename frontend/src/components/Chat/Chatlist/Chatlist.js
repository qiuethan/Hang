import React, { useEffect } from "react";
import { useDispatch, useSelector } from "react-redux";
import { loadrooms } from "../../../actions/chat";
import Chatitem from "./Chatitem/Chatitem";

const Chatlist = ({ currentRoom, setCurrentRoom, clientOpened }) => {
    
    const dispatch = useDispatch();

    const rooms = useSelector(state => state.dms);

    useEffect(() => {
        if(clientOpened){ 
            dispatch(loadrooms());
        }
    }, [currentRoom, clientOpened]);

    return(
        (rooms.length === 0) ?  <div/>: <div>
            {rooms.map((room) => 
                <Chatitem key={room.id} roomid = {room.id} users = {JSON.stringify(room.users)} type = {room.channel_type} setCurrentRoom = {setCurrentRoom}/>
            )}
        </div>
    );
}

export default Chatlist;