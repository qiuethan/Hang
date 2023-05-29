import React, {useEffect} from "react";
import {useNavigate, useSearchParams} from "react-router-dom";
import {joinhangevent} from "../../../../actions/hang";
import {useDispatch} from "react-redux";

const Join = () => {

    const [searchParams, setSearchParams] = useSearchParams();
    const navigate = useNavigate();

    const dispatch = useDispatch();

    const getCode = () => {
        return searchParams.get("code");
    }

    useEffect(() => {
        const code = getCode();
        dispatch(joinhangevent(code, navigate));
    }, []);

    return(
        <div>

        </div>
    )
}

export default Join;