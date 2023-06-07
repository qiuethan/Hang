/*
Author: Ethan Qiu
Filename: Locaiton.js
Last Modified: June 7, 2023
Description: Allows user to see + edit location
*/

import React, {useState} from "react";

import Search from "./Address/Search";
import MapComponent from "./GoogleMap/MapComponent";
import {Box} from "@mui/material";

//Location component
const Location = ({fields, setFields, updateLocation}) => {

    //Render component
    return(
        <Box sx={{display: "flex", width: "100%", height: "100%", flexDirection: "column", justifyContent:"center", alignItems:"center"}}>
            <Search fields={fields} address={fields.address} setFields={setFields} updateLocation={updateLocation}/>
            <MapComponent updateLocation={updateLocation} fields={fields} setFields={setFields}/>
        </Box>
    )
}

export default Location;