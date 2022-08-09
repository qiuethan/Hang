import React, { useEffect } from "react";
import { useDispatch, useSelector } from "react-redux";
import { loadfriends } from "../../actions/friends";
import Friendlist from "./Friendlist/Friendlist";

const Friends = () => {

    const dispatch = useDispatch();

    useEffect(() => {
        dispatch(loadfriends());
    }, [])

    return(
        <Friendlist/>
    );
}

export default Friends;