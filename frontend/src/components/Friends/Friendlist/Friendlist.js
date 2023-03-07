import React, { useEffect, useState } from "react";
import { useSelector } from "react-redux";
import Friend from "./Friend/Friend";

const Friendlist = () => {

    const friends = useSelector(state => state.friends);

    console.log(friends);

    return(
        friends.length === 0 ? <div/> : <div>
            {friends.map((friend) => (
                <Friend key={friend} friend={friend}/>
            ))}
        </div>
    );
}

export default Friendlist;