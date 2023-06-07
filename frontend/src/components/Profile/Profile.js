import React, {useEffect} from "react";
import {useSelector, useDispatch} from "react-redux";
import {useNavigate} from "react-router-dom";
import {getself} from "../../actions/users";
import User from "./User/User";
import {Box, Paper} from "@mui/material";
import Calendar from "./Calendar/Calendar";

const Profile = ({currentPage, setCurrentPage}) => {

    const user = useSelector(state => state.profile);
    console.log(user);

    const dispatch = useDispatch();

    console.log(JSON.parse(localStorage.getItem("profile")));

    const navigate = useNavigate();

    useEffect(() => {
        if(JSON.parse(localStorage.getItem("profile")) === null){
            navigate("/auth");
        }
    }, [localStorage.getItem("profile")]);

    useEffect(() => {
        dispatch(getself());
    }, [])

    return(
        <Box sx={{display: "flex", width: "100%", height: "100%", justifyContent: "center", alignItems: "center"}}>
            <Paper elevation={16} sx={{display:"flex", width: "98%", height: "96%", alignItems: "center", justifyContent: "center", borderRadius: "10px"}}>
                <Box sx={{display: "flex", width: "98%", height: "90%", flexDirection: "column", alignItems: 'center'}}>
                    <Box sx={{display: "flex", justifyContent: "center", width: "100%", height: "40%", marginBottom: "20px"}}>
                        <User/>
                    </Box>
                    <Box sx={{display: "flex", width: "90%", justifyContent: "center", height: "60%"}}>
                        <Calendar/>
                    </Box>
                </Box>
            </Paper>
        </Box>
    )
}

export default Profile;