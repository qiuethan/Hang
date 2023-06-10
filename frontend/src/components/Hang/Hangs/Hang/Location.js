/*
Author: Ethan Qiu
Filename: Locaiton.js
Last Modified: June 7, 2023
Description: Display locaiton of Hang on mini map
*/

import React, {useEffect, useState} from "react";
import { GoogleMap, LoadScript, Marker } from '@react-google-maps/api';
import {Box} from "@mui/material";

//Set size + style of map
const containerStyle = {
    width: '100%',
    height: '100%',
    borderRadius: "5px",
};

//Map component
const MapComponent = ({details}) => {

    //Render component
    return(
        <Box sx={{display: "flex", width: "calc(100% - 5px)", height: "390px", bgcolor: "#a5d6b0", borderRadius: "10px", marginLeft: "5px"}}>
            <Box sx={{display: "flex", flexDirection: "column", width: "calc(100% - 20px)", margin: "10px", alignItems: "center"}}>
                <GoogleMap
                    mapContainerStyle={containerStyle}
                    center={{lat: +details.latitude, lng: +details.longitude}}
                    zoom={16}
                >
                    <Marker position={{lat: +details.latitude, lng: +details.longitude}}/>
                </GoogleMap>
            </Box>
        </Box>
    );
}

export default MapComponent;