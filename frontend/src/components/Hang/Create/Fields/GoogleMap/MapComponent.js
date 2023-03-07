import React, {useEffect, useState} from "react";

import { GoogleMap, LoadScript, Marker } from '@react-google-maps/api';

const containerStyle = {
    width: '400px',
    height: '400px'
};

const MapComponent = ({latitude, longitude, updateLocation }) => {

    const handleClick = (e) => {
        updateLocation(e.latLng.lat(), e.latLng.lng());
    };

    return(
        <GoogleMap
                mapContainerStyle={containerStyle}
                center={{lat: +latitude, lng: +longitude}}
                zoom={16}
                onClick={handleClick}
            >
                <Marker position={{lat: +latitude, lng: +longitude}}/>
        </GoogleMap>

    );
}

export default MapComponent;