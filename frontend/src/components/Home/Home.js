import React from "react";
import * as actionTypes from "../../constants/actionTypes"; 
import { useState } from "react";
import { useDispatch } from "react-redux";
import { useNavigate } from "react-router-dom";

const Home = () => {

    const dispatch = useDispatch();
    const history = useNavigate();

    const [user, setUser] = useState(JSON.parse(localStorage.getItem('profile')));

    console.log(localStorage.getItem('profile'))

    const logout = () => {
        dispatch({type: actionTypes.LOGOUT})

        history('/auth');

        setUser(null);
    }

    return(
        <div>
            <h1>Welcome to Hang!</h1>
            {
                !(user == null) && 
                <>
                    <button onClick={logout}>Logout</button>
                </>
            }
        </div>
    );
};

export default Home