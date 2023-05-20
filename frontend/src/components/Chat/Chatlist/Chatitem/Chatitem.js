import React, { useEffect, useState } from "react";
import { useDispatch, useSelector} from "react-redux";
import {getuser} from "../../../../actions/users";
import {Avatar, Box, Button} from "@mui/material";

const Chatitem = ({ roomid, users, type, gcName, currentRoom, setCurrentRoom }) => {

    const dispatch = useDispatch();

    const handleClick = (event) => {
        event.preventDefault();
        setCurrentRoom(roomid);
    }

    const userStorage = useSelector(state => state.users);

    const [name, setName] = useState("");
    const [picture, setPicture] = useState("");

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
                    setPicture(obj.profile_picture);
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
        <Box sx={{width: "100%", height: "60px"}}>
            <Button
                disableRipple
                onClick={handleClick}
                sx={{width: "100%", height: "100%", "&:hover": {backgroundColor: "#a5d6b0"}, borderRadius: "0", backgroundColor: roomid === currentRoom ? "#0c7c59" : ""}}
            >
                <Box sx={{display: "flex", flexDirection: "row", width: "100%"}}>
                    <Box sx={{width: "20%", height: "100%"}}>
                        <Avatar src={picture} sx={{aspectRatio: "1"}}/>
                    </Box>
                    <h3 style={{margin: "0", alignSelf:"center", marginLeft: "10px", color: roomid === currentRoom ? "white" : "black", overflowX: "scroll"}}>{name}</h3>
                </Box>
            </Button>
        </Box>

    );
};

export default Chatitem;