import React, { useState } from 'react';

import { Box, Grid, TextField, IconButton } from '@mui/material';
import SendIcon from '@mui/icons-material/Send';

const Form = ({ client, currentRoom }) => {

    const [message, setMessage] = useState("");

    const messageSend = (event) => {
        try{
            event.preventDefault();
        }
        catch (error){}

        if(message.trim() !== ""){
            client.send(JSON.stringify({
                action: "send_message",
                content: {
                    message_channel: {
                        id: currentRoom
                    },
                    content: message
                }
            }));
    
            setMessage("");
        }
    }

    const handleChange = (event) => {
        setMessage(event.target.value);
    }

    return(
        <Box sx={{bgcolor:"#0c7c59"}}>
            {
                JSON.parse(localStorage.getItem('profile') !== null) &&
                <form onSubmit={messageSend}>
                    <Grid container direction="row" sx={{p:1.5}}>
                        <Grid item xs={7} sm={8} md={9} lg={10}>
                            <TextField 
                                label={message==="" ? `Message ${currentRoom}` : ""} 
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
                                maxRows={5}
                                sx={{marginRight: 1, borderRadius: "10px", bgcolor: "white", width:"98%", "& .MuiOutlinedInput-root":{"& > fieldset": {border: "none"}},"& .MuiInputLabel-root":{color: "#0c7c59"}, "& label.Mui-focused": {color: "black"}}}
                            />
                        </Grid>
                        <Grid item xs={5} sm={4} md={3} lg={2}>
                            <Grid container direction="row" justifyContent="center" sx={{marginLeft: 1}}>
                                <Grid item xs={4}>
                                    <IconButton 
                                        variant="contained"
                                        disableElevation
                                        sx={{bgcolor : "white", color: "#0c7c59", "&:hover": {bgcolor: "#a5d6b0", color: "white"}, borderRadius: "10px", height: "40px", minWidth: "40px"}}
                                    >
                                    </IconButton>
                                </Grid>
                                <Grid item xs={4}>
                                    <IconButton 
                                        variant="contained"
                                        disableElevation
                                        sx={{bgcolor : "white", color: "#0c7c59", "&:hover": {bgcolor: "#a5d6b0", color: "white"}, borderRadius: "10px", height: "40px", minWidth: "40px"}}
                                    >
                                    </IconButton>
                                </Grid>
                                <Grid item xs={4}>
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