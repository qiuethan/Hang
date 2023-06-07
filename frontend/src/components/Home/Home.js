/*
Author: Ethan Qiu
Filename: Home.js
Last Modified: June 7, 2023
Description: Home page
*/

import React, {useEffect} from "react";
import { useState, getState } from "react";
import { useDispatch, useSelector } from "react-redux";
import { useNavigate } from "react-router-dom";
import { logout } from "../../actions/login";

//Home component
const Home = ({}) => {

    //Define dispatch variable
    const dispatch = useDispatch();

    //Define history variable
    const history = useNavigate();

    //Set user to localstorage object
    const [user, setUser] = useState(JSON.parse(localStorage.getItem('profile')));

    //Define navigation variable
    const navigate = useNavigate();

    //On render
    useEffect(() => {
        //If not logged in, send to auth
        if(JSON.parse(localStorage.getItem("profile")) === null || JSON.parse(localStorage.getItem("profile")) === undefined){
            navigate("/auth");
        }
    }, [localStorage.getItem("profile")]);

    //When user presses log out button
    const logOut = () => {
        //Send logout to API
        dispatch(logout(user.token))
        .then((response) => {
            //Deletes localstorage
            localStorage.clear();
        })

        //Sets user to null
        setUser(null);

        //Navigate to auth
        history('/auth');
    }

    //Render components
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

export default Home;