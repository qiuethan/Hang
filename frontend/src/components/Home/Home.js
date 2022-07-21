import React from "react";
import * as actionTypes from "../../constants/actionTypes"; 
import { useState, getState } from "react";
import { useDispatch } from "react-redux";
import { useNavigate } from "react-router-dom";
import { logout } from "../../actions/login";

const Home = () => {

    const dispatch = useDispatch();
    const history = useNavigate();

    const [user, setUser] = useState(JSON.parse(localStorage.getItem('profile')));

    console.log(user);

    const logOut = () => {
        dispatch(logout(user.token))

        history('/auth');

        setUser(null);

        localStorage.clear();
    }

    return(
        <div>
            <h1>Welcome to Hang!</h1>
            {
                !(user == null) && 
                <>
                    <button onClick={logOut}>Logout</button>
                </>
            }
        </div>
    );
};

export default Home