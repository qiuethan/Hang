import React, { useEffect, useState } from "react";
import { useSelector } from "react-redux";

import Request from "./Request/Request";

const Sentlist = () => {

    const requests = useSelector((state) => state.sentrequests);

    console.log(requests);

    return(
        requests.length === 0 ? <div/> : <div>
            {requests.map((request) => (
                !request.declined && (
                    <Request key={request.to_user} user={request.to_user}/>
                )
            ))}
        </div>
    )
}

export default Sentlist;