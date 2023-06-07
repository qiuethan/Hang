import React, {useEffect, useState} from "react";

import { GoogleMap, LoadScript, Marker } from '@react-google-maps/api';
import {Box} from "@mui/material";

const containerStyle = {
    width: '100%',
    height: '100%',
    borderRadius: "5px",
};

const MapComponent = ({details}) => {

    const sendToGoogle = () => {
        window.open(`https://www.google.com/maps/dir/?api=1&destination=${details.address}`)
    }

    return(
        <Box sx={{display: "flex", width: "100%", height: "390px", bgcolor: "#a5d6b0", borderRadius: "10px"}}>
            <Box sx={{display: "flex", flexDirection: "column", width: "100%", margin: "10px", alignItems: "center"}}>
                <Box sx={{marginBottom: "10px"}}>{details.address}</Box>
                <GoogleMap
                    mapContainerStyle={containerStyle}
                    center={{lat: +details.latitude, lng: +details.longitude}}
                    zoom={16}
                    onClick={sendToGoogle}
                >
                    <Marker position={{lat: +details.latitude, lng: +details.longitude}}/>
                </GoogleMap>
            </Box>
        </Box>
    );
}

export default MapComponent;