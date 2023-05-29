import React, { useEffect } from "react";
import {useNavigate, useSearchParams} from "react-router-dom";

import axios from "axios";

const Verify = () => {

    const [searchParams, setSearchParams] = useSearchParams();

    const navigate = useNavigate();

    const API = axios.create({ baseURL: 'http://localhost:8000'})

    const getKey = () => {
        return searchParams.get("key");
    }
    const validate = async (key) => {
        try{
            await API.delete(`/v1/accounts/email_verification_tokens/${key}/`);
        }
        catch(error){
            console.log(error);
        }
    }

    const returnToAuth = () => {
        navigate("/auth");
    }

    useEffect(() => {
        const key = getKey();
        validate(key).then((response) => console.log(response));
    }, []);

    return(
        <div>
            <div>Verified</div>
            <button onClick={returnToAuth}>Click here to return to login page</button>
        </div>
    );
};

export default Verify;