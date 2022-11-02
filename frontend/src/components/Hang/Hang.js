import React from "react";
import { Route, Routes } from "react-router-dom";
import Create from "./Create/Create";

const Hang = ({currentPage, setCurrentPage}) => {
    return (
        <Routes>
            <Route path="/create" element={<Create currentPage={currentPage} setCurrentPage={setCurrentPage}/>}/>  
        </Routes> 
    );
}

export default Hang;