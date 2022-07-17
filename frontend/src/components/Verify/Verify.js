import React, { useEffect } from "react";
import { useSearchParams } from "react-router-dom";

import axios from "axios";

const Verify = () => {

    const[searchParams, setSearchParams] = useSearchParams();
    
    const API = axios.create({ baseURL: 'http://localhost:8000'})

    const validate = (key) => API.post('/auth/verify_email', {token: key} )

    useEffect(() => {
        const key = searchParams.get("key");
        validate(key);
    });

    return(
        <div>Verified</div>
    );
};

export default Verify;