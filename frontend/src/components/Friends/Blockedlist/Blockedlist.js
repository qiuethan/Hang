import React, { useEffect, useState } from "react";
import Blocked from "./Blocked/Blocked";
import {useSelector} from "react-redux";

const Blockedlist = () => {

    const blocked = useSelector(state => state.blocked);

    console.log(blocked);

    return(
        blocked.length === 0 ? <div/> : <div>
            {blocked.map((blocked) => (
                <Blocked key={blocked} blocked={blocked}/>
            ))}
        </div>
    );
}

export default Blockedlist;