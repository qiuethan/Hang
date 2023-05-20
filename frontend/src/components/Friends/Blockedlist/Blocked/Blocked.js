import React, {useState, useEffect} from "react";
import {useDispatch, useSelector} from "react-redux";
import {getuser} from "../../../../actions/users";
import {unblockeduser} from "../../../../actions/friends";
import {Avatar, Box, Button} from "@mui/material";

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
            setUser(obj);
        }
    }, [useSelector((state) => state.users)])


    const unblock = () => {
        dispatch(unblockeduser(blocked));
    }

    return(
        <Box sx={{display: "flex", width: "99.5%", height: "65px", alignItems: "center", marginTop: "5px", borderTop: '0.5px solid black'}}>
            <Box sx={{display: "flex", width: "100%", height: "60px", alignItems: "center", ":hover": {bgcolor: "#a5d6b0"}, borderRadius: "10px", marginTop: "5px"}}>
                <Box sx={{display: "flex", width: "50%", height: "90%", alignItems: "center", marginLeft: "10px"}}>
                    <Avatar src={user.profile_picture} sx={{height: "40px", width: "40px"}}/>
                    <h3 style={{margin: "0", fontSize: "20px", marginLeft: "10px"}}>{user !== "" && (user.user.username)}</h3>
                </Box>
                <Box sx={{display: "flex", width: "50%", height: "100%", alignItems: "center", justifyContent: "flex-end", marginRight: "10px"}}>
                    <Button onClick={unblock} sx={{backgroundColor: 'transparent', color: "black",':hover': {backgroundColor: 'transparent'} }}>Unblock</Button>
                    </Box>
            </Box>
        </Box>
    );
}

export default Blocked;