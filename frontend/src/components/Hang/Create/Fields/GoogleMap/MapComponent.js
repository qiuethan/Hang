import React, {useEffect, useState} from "react";

import { GoogleMap, LoadScript, Marker } from '@react-google-maps/api';

const containerStyle = {
    width: '400px',
    height: '400px'
};

const MapComponent = ({latitude, longitude}) => {

    return(
        <LoadScript googleMapsApiKey="AIzaSyDnfmoE9jAHUxXhTvytcPBjQTntcOBKzwQ">
            <GoogleMap
                mapContainerStyle={containerStyle}
                center={{lat: +latitude, lng: +longitude}}
                zoom={16}
            >
                <Marker position={{lat: +latitude, lng: +longitude}}/>
            </GoogleMap>
        </LoadScript>
    );
}

export default MapComponent;