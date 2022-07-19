import React, { useEffect } from "react";
import { useSearchParams } from "react-router-dom";

import axios from "axios";

const Verify = () => {

    const[searchParams, setSearchParams] = useSearchParams();
    
    const API = axios.create({ baseURL: 'http://localhost:8000'})

    const validate = async (key) => {
        try{
            await API.post('/auth/verify_email', {token: key} );
        }
        catch(error){
            console.log(error);
        }
    }

    useEffect(() => {
        const key = searchParams.get("key");
        validate(key).then((response) => console.log(response));
    });

    return(
        <div>Verified</div>
    );
};

export default Verify;