import React, { useEffect } from "react";
import { useDispatch, useSelector } from "react-redux";
import { loadfriends, loadrecievedfriendrequests } from "../../actions/friends";
import Friendlist from "./Friendlist/Friendlist";
import Requestlist from "./Requestlist/Requestlist";

const Friends = () => {

    const dispatch = useDispatch();

    useEffect(() => {
        dispatch(loadfriends());
        dispatch(loadrecievedfriendrequests());
    }, [])

    console.log(useSelector((state) => state));

    return(
        <div>
            <Friendlist/>
            <Requestlist/>
        </div>
        
    );
}

export default Friends;