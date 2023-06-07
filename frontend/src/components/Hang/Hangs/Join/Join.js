/*
Author: Ethan Qiu
Filename: Join.js
Last Modified: June 7, 2023
Description: Allow users to join hang
*/

import React, {useEffect} from "react";
import {useNavigate, useSearchParams} from "react-router-dom";
import {addtocalendar, joinhangevent} from "../../../../actions/hang";
import {useDispatch} from "react-redux";
import {FRONTENDURL} from "../../../../constants/actionTypes";

//Join component
const Join = () => {

    //Define search parameter variables
    const [searchParams, setSearchParams] = useSearchParams();

    //Define navigation variable
    const navigate = useNavigate();

    //Define dispatch variable
    const dispatch = useDispatch();

    //Get code from search parameters
    const getCode = () => {
        return searchParams.get("code");
    }

    //On render
    useEffect(() => {
        //Get join code
        const code = getCode();
        //Send join event to server and save response
        dispatch(joinhangevent(code, navigate)).then((r) =>{
            if(r !== undefined){
                //If response == success, add to calendar
                dispatch(addtocalendar(r.id)).then((response) => {
                    //Send user to other link
                    window.location.href = `${FRONTENDURL}hang?room=${r.id}`
                    window.location.reload();
                })
            }
            else{
                //Go back to hang page
                navigate("/hang");
            }
        });

    }, []);

    //No components to render
    return(
        <div>

        </div>
    )
}

export default Join;