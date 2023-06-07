import React, {useEffect} from "react";
import {useNavigate, useSearchParams} from "react-router-dom";
import {joinhangevent} from "../../../../actions/hang";
import {useDispatch} from "react-redux";
import {FRONTENDURL} from "../../../../constants/actionTypes";

const Join = () => {

    const [searchParams, setSearchParams] = useSearchParams();
    const navigate = useNavigate();

    const dispatch = useDispatch();

    const getCode = () => {
        return searchParams.get("code");
    }

    useEffect(() => {
        const code = getCode();
        dispatch(joinhangevent(code, navigate)).then((r) =>{
            if(r !== undefined){
                window.location.href = `${FRONTENDURL}hang?room=${r.id}`
                window.location.reload();
            }
            else{
                navigate("/hang/");
            }
        });

    }, []);

    return(
        <div>

        </div>
    )
}

export default Join;