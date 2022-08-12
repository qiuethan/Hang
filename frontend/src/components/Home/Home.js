import React from "react";
import * as actionTypes from "../../constants/actionTypes"; 
import { useState, getState } from "react";
import { useDispatch, useSelector } from "react-redux";
import { useNavigate } from "react-router-dom";
import { logout } from "../../actions/login";

const Home = ({}) => {

    const dispatch = useDispatch();
    const history = useNavigate();

    const [user, setUser] = useState(JSON.parse(localStorage.getItem('profile')));

    console.log(user);

    console.log(useSelector(state => state));

    const logOut = () => {
        dispatch(logout(user.token))
        .then((response) => {
            console.log(response);
            localStorage.clear();
            console.log(localStorage);
        })

        setUser(null);

        history('/auth');
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