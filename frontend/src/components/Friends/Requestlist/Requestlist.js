import React, { useEffect, useState } from "react";
import { useSelector } from "react-redux";

import Request from "./Request/Request";

const Requestlist = () => {

    const requests = useSelector((state) => state.friendrequests);

    console.log(requests);

    return(
        requests.length === 0 ? <div/> : <div>
            {requests.map((request) => (
                !request.declined && (
                    <Request key={request.from_user} user={request.from_user}/>
                )
            ))}
        </div>
    )
}

export default Requestlist;