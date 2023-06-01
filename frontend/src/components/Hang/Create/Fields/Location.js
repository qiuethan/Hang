import React, {useState} from "react";

import Search from "./Address/Search";
import MapComponent from "./GoogleMap/MapComponent";
import {Box} from "@mui/material";

const Location = ({fields, setFields, updateLocation}) => {


    return(
        <Box sx={{display: "flex", width: "100%", height: "100%", flexDirection: "column", justifyContent:"center", alignItems:"center"}}>
            <Search fields={fields} address={fields.address} setFields={setFields} updateLocation={updateLocation}/>
            <MapComponent updateLocation={updateLocation} fields={fields} setFields={setFields}/>
        </Box>
    )
}

export default Location;