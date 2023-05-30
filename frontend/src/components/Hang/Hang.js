import React, {useEffect} from "react";
import {Route, Routes, useNavigate} from "react-router-dom";

import Hangs from "./Hangs/Hangs";
import Create from "./Create/Create";
import Join from "./Hangs/Join/Join";

const Hang = ({currentPage, setCurrentPage}) => {

    const navigate = useNavigate();

    useEffect(() => {
        if(JSON.parse(localStorage.getItem("profile")) === null){
            navigate("/auth");
        }
    }, [localStorage.getItem("profile")]);

    return (
        <Routes>
            <Route path="/" element={<Hangs currentPage={currentPage} setCurrentPage={setCurrentPage}/>}/>
            <Route path="/create" element={<Create currentPage={currentPage} setCurrentPage={setCurrentPage}/>}/>
            <Route path="/join" element={<Join/>}/>
        </Routes> 
    );
}

export default Hang;