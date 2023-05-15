import React, {useState} from "react";

import Search from "./Address/Search";
import MapComponent from "./GoogleMap/MapComponent";
import {Box} from "@mui/material";

const Location = ({longitude, latitude, updateLocation}) => {

    const [address, setAddress] = useState("");

    const changeAddress = (e) => {
        e.preventDefault();
        setAddress(e.target.value);
    }

    return(
        <Box sx={{display: "flex", width: "100%", height: "100%", flexDirection: "column", justifyContent:"center", alignItems:"center"}}>
            <Search updateLocation={updateLocation}/>
            <MapComponent latitude={latitude} longitude={longitude} updateLocation={updateLocation}/>
        </Box>
    )
}

export default Location;