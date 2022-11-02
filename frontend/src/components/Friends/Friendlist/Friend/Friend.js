import React from "react";
import { useDispatch } from "react-redux";
import { blockfriend, removefriend } from "../../../../actions/friends";

const Friend = ({friend}) => {

    const dispatch = useDispatch();

    const remove = (e) => {
        e.preventDefault();
        dispatch(removefriend(friend));
    }

    const block = (e) => {
        e.preventDefault();
        dispatch(blockfriend(friend));
    }

    return(
        <div>
            {friend.username}
            <button onClick={remove}>Remove Friend</button>
            <button onClick={block}>Block</button>
        </div>
    );
}

export default Friend;