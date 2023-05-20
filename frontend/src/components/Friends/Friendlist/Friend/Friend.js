import React, {useState, useEffect} from "react";
import {useDispatch, useSelector} from "react-redux";
import { blockfriend, removefriend } from "../../../../actions/friends";
import {getuser} from "../../../../actions/users";
import {Avatar, Box, Button} from "@mui/material";

const Friend = ({friend}) => {

    const dispatch = useDispatch();

    console.log(friend);

    const [user, setUser] = useState("");

    const users = useSelector(state => state.users);

    console.log(user);

    useEffect(() => {
        const obj = users.find((user) => user.user.id === friend)
        if(obj === undefined){
            console.log("Sent to Server");
            dispatch(getuser(friend));
        }
        else{
            setUser(obj);
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
        <Box sx={{display: "flex", width: "99.5%", height: "65px", alignItems: "center", marginTop: "5px", borderTop: '0.5px solid black'}}>
            <Box sx={{display: "flex", width: "100%", height: "60px", alignItems: "center", ":hover": {bgcolor: "#a5d6b0"}, borderRadius: "10px", marginTop: "5px"}}>
                <Box sx={{display: "flex", width: "50%", height: "90%", alignItems: "center", marginLeft: "10px"}}>
                    <Avatar src={user.profile_picture} sx={{height: "40px", width: "40px"}}/>
                    <h3 style={{margin: "0", fontSize: "20px", marginLeft: "10px"}}>{user !== "" && (user.user.username)}</h3>
                </Box>
                <Box sx={{display: "flex", width: "50%", height: "100%", alignItems: "center", justifyContent: "flex-end", marginRight: "10px"}}>
                    <Button onClick={remove} sx={{backgroundColor: 'transparent', color: "black",':hover': {backgroundColor: 'transparent'} }}>Remove Friend</Button>
                    <Button onClick={block} sx={{backgroundColor: 'transparent', color: "red",':hover': {backgroundColor: 'transparent'}}}>Block</Button>
                </Box>
            </Box>
        </Box>
    );
}

export default Friend;