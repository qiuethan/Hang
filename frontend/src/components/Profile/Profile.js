import React, {useEffect} from "react";
import {useSelector, useDispatch} from "react-redux";
import {useNavigate} from "react-router-dom";
import {getself} from "../../actions/users";
import Google from "./Google/Google";
import User from "./User/User";
import {Box} from "@mui/material";

const Profile = ({currentPage, setCurrentPage}) => {

    const user = useSelector(state => state.profile);
    console.log(user);

    const dispatch = useDispatch();

    console.log(JSON.parse(localStorage.getItem("profile")));

    const navigate = useNavigate();

    useEffect(() => {
        setCurrentPage("profile");
        if(JSON.parse(localStorage.getItem('profile')) == null){
            navigate("/auth")
        }
    }, [currentPage]);

    useEffect(() => {
        dispatch(getself());
    }, [])

    return(
        <Box sx={{display: "flex", width: "100%", height: "100%", justifyContent: "center", alignItems: "center"}}>
            <Box sx={{display:"flex", width: "98%", height: "95%", flexDirection:"column", overflowY:"scroll"}}>
                <User/>
                <Google/>
            </Box>
        </Box>
    )
}

export default Profile;