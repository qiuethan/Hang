import React, {useEffect, useState} from "react";
import {Box, Button} from "@mui/material";
import {useDispatch, useSelector} from "react-redux";
import {getuser} from "../../../../actions/users";
import SettingsIcon from "@mui/icons-material/Settings";

const Settings = ({currentRoom, settings, setSettings}) => {

    const dispatch = useDispatch();

    const user = JSON.parse(localStorage.getItem('profile'));
    const allUsers = useSelector(state => state.users);

    const [otherUser, setOtherUser] = useState("");

    const dmDetails = useSelector(state => state.dms).filter(room => room.id === currentRoom)[0];
    const groupDetails = useSelector(state => state.groups).filter(room => room.id === currentRoom)[0];

    useEffect(() => {
        if(dmDetails){
            const dmUser = allUsers.find(u => u.user.id === dmDetails.users.filter(u => u !== user.user.id)[0]);
            if(!dmUser){
                console.log("Sent to Server");
                dispatch(getuser(dmDetails.users.filter(u => u !== user.user.id)[0]));
            }
            else{
                setOtherUser(dmUser);
                console.log(dmUser);
            }
        }
    }, [useSelector((state) => state.users), currentRoom])

    const [buttonHover, setButtonHover] = useState(false);

    const handleSettings = () => {
        setSettings(!settings);
    }

    return(
        <Box sx={{display: "flex", height: "100%", width: "100%", bgcolor:"#0c7c59", alignItems: "center", justifyContent: "center", borderRadius: "10px 10px 0 0"}}>
            {dmDetails && (
                <Box sx={{display: "flex", flexDirection: "row", height: "80%", width: "98%"}}>
                    <Box sx={{display: "flex", width: "50%", height: "100%", alignItems: "center"}}>
                        {otherUser !== "" && (
                            <h3 style={{margin: "0", color: "white"}}>{otherUser.user.username}</h3>
                        )}
                    </Box>
                </Box>
            )}
            {groupDetails && (
                <Box sx={{display: "flex", flexDirection: "row", height: "80%", width: "98%"}}>
                    <Box sx={{display: "flex", width: "50%", height: "100%", alignItems: "center"}}>
                        <h3 style={{margin: "0", color: "white"}}>{groupDetails.name}</h3>
                    </Box>
                    <Box sx={{display: "flex", flexDirection: "row-reverse", alignItems:"center", width: "50%", height: "100%"}}>
                        <Button onClick={handleSettings} disableRipple onMouseEnter={() => setButtonHover(true)} onMouseLeave={() => setButtonHover(false)}><SettingsIcon sx={{color: buttonHover ? "#a5d6b0" : "white"} }/></Button>
                    </Box>
                </Box>
            )}
        </Box>
    )
}

export default Settings;