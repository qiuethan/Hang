import React, { useEffect } from "react";
import { useDispatch, useSelector } from "react-redux";
import { loadgroups } from "../../../actions/chat";
import Chatitem from "./Chatitem/Chatitem";
import {Box, Paper} from "@mui/material";

const Grouplist = ({ currentRoom, setCurrentRoom, clientOpened }) => {
    
    const dispatch = useDispatch();

    const rooms = useSelector(state => state.groups);

    useEffect(() => {
        dispatch(loadgroups());
    }, [currentRoom, clientOpened]);

    return(
        <Paper elevation={16} sx={{display: "flex", flexDirection: "column", height: "50%", width: "96%", borderRadius: "0 0 10px 10px"}}>
            <Box sx={{display: "flex", flexDirection: "row", width: "100%", height: "10%", alignItems: "center", justifyContent: "center", bgcolor: "#0c7c59", borderRadius: "0 0 0 0"}}>
                <h3 style={{margin: "0", color: "white"}}>Group Chats</h3>
            </Box>
            <Box sx={{display: "block", width: "100%", height: "90%"}}>
                {(rooms.length === 0) ?  <Box/>: <Box sx={{display: "flex", flexDirection: "column", height: "100%", overflowY: "scroll"}}>
                    {rooms.map((room) =>
                        <Chatitem key={room.id} roomid = {room.id} users = {JSON.stringify(room.users)} type = {room.channel_type} currentRoom = {currentRoom} setCurrentRoom = {setCurrentRoom} gcName={room.name}/>
                    )}
                </Box>}
            </Box>
        </Paper>
    );
}

export default Grouplist;