import React, {useEffect} from "react";
import {useSelector, useDispatch} from "react-redux";
import {useNavigate} from "react-router-dom";
import {getself} from "../../actions/users";
import Google from "./Google/Google";

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
        <div>
            <Google/>
        </div>
    )
}

export default Profile;