import React, {useEffect, useState} from 'react';

import { Box, Grid, TextField, IconButton } from '@mui/material';
import SendIcon from '@mui/icons-material/Send';
import {useDispatch, useSelector} from "react-redux";
import {getuser} from "../../../../actions/users";

const Form = ({ client, currentRoom }) => {

    const [message, setMessage] = useState("");

    const dispatch = useDispatch();

    const messageSend = (event) => {
        try{
            event.preventDefault();
        }
        catch (error){}

        if(message.trim() !== ""){
            client.send(JSON.stringify({
                action: "send_message",
                content: {
                    message_channel: currentRoom,
                    content: message,
                    reply: null
                }
            }));
    
            setMessage("");
        }
    }

    const handleChange = (event) => {
        setMessage(event.target.value);
    }

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

    return(
        <Box sx={{height: "100%", display: "flex", borderRadius: "0 0 10px 0", alignItems: "center"}}>
            {
                JSON.parse(localStorage.getItem('profile') !== null) &&
                <form onSubmit={messageSend}>
                    <Grid container direction="row" sx={{p:1.5}}>
                        <Grid item xs={8} sm={9} md={10} lg={11}>
                            <TextField 
                                label={message==="" ? `Message ${otherUser !== "" && dmDetails ? otherUser.user.username : groupDetails ? groupDetails.name : ""}` : ""}
                                value={message || ""} 
                                onChange={handleChange} 
                                onKeyDown={(e) => {
                                    if(e.code === "Enter" && !e.shiftKey){
                                        messageSend();
                                        e.preventDefault();
                                    }

                                }}
                                InputProps={{
                                    form:{
                                        autocomplete: 'off',
                                    },
                                }}
                                InputLabelProps={{shrink: false}}
                                multiline
                                size="small"
                                maxRows={1}
                                sx={{marginRight: 1, borderRadius: "10px", bgcolor: "white", width:"100%", "& .MuiOutlinedInput-root":{"& > fieldset": {border: "none"}},"& .MuiInputLabel-root":{color: "#0c7c59"}, "& label.Mui-focused": {color: "black"}}}
                            />
                        </Grid>
                        <Grid item xs={4} sm={3} md={2} lg={1}>
                            <Grid container direction="row" justifyContent="center" sx={{marginLeft: 1}}>
                                <Grid item xs={6}>
                                    <IconButton 
                                        variant="contained"
                                        disableElevation
                                        sx={{bgcolor : "white", color: "#0c7c59", "&:hover": {bgcolor: "#a5d6b0", color: "white"}, borderRadius: "10px", height: "40px", minWidth: "40px"}}
                                    >
                                    </IconButton>
                                </Grid>
                                <Grid item xs={6}>
                                    <IconButton 
                                        type="submit"
                                        variant="contained"
                                        disableElevation
                                        sx={{bgcolor : "white", color: "#0c7c59", "&:hover": {bgcolor: "#a5d6b0", color: "white"}, borderRadius: "10px", height: "40px", minWidth: "40px"}}
                                    >
                                        <SendIcon sx={{height: "20px", width: "20px"}}/>
                                    </IconButton>
                                </Grid>
                            </Grid>
                            
                        </Grid>
                    </Grid>
                </form>
            }
        </Box>
    );
};

export default Form;