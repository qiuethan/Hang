import React from "react";
import { Route, Routes } from "react-router-dom";

import Hangs from "./Hangs/Hangs";
import Create from "./Create/Create";


const Hang = ({currentPage, setCurrentPage}) => {
    return (
        <Routes>
            <Route path="/" element={<Hangs currentPage={currentPage} setCurrentPage={setCurrentPage}/>}/>
            <Route path="/create" element={<Create currentPage={currentPage} setCurrentPage={setCurrentPage}/>}/>  
        </Routes> 
    );
}

export default Hang;