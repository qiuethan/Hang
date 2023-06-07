import React, {useEffect, useState} from "react";
import {Box, Checkbox} from "@mui/material";

const UserCalendar = ({calendar, synchedCalendars, setSynchedCalendars}) => {

    const [checked, setChecked] = useState(calendar.previous);

    useEffect(() => {
        console.log(synchedCalendars);
    }, [synchedCalendars]);

    const onChecked = () => {
        if(checked){
            setChecked(false);
            setSynchedCalendars(synchedCalendars.filter((c) => c.id !== calendar.google_calendar_id))
            console.log(synchedCalendars);
        }
        else{
            setChecked(true);
            setSynchedCalendars([...synchedCalendars, {
                id: calendar.google_calendar_id,
                name: calendar.name
            }]);
            console.log(synchedCalendars);
        }
    }

    return(
        <Box sx={{alignItems: "center", display: "flex", flexDirection: "row", width: "100%", height: "60px", borderTop: "1px black solid", bgcolor: calendar.previous ? "#a5d6b0" : "white", }}>
            <Box sx={{width: "50%"}}>
                <p style={{margin: '0', fontSize: "16px", marginLeft: "10px"}}>{calendar.name}</p>
            </Box>
            <Box sx={{display: "flex", width: "50%", justifyContent: "flex-end"}}>
                <Checkbox defaultChecked={calendar.previous} sx={{color: "#0c7c59", '&.Mui-checked': {color: "#0c7c59"}, marginRight: "10px"}} onClick={onChecked}/>
            </Box>
        </Box>
    )
}

export default UserCalendar;