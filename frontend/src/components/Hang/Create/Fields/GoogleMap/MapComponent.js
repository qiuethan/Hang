import React, {useEffect, useState} from "react";

import { GoogleMap, LoadScript, Marker } from '@react-google-maps/api';

const containerStyle = {
    width: '800px',
    height: '500px'
};

const MapComponent = ({latitude, longitude, updateLocation }) => {

    const handleClick = (e) => {
        const geocoder = new window.google.maps.Geocoder();

        const lat = e.latLng.lat();
        const lng = e.latLng.lng();
        updateLocation(lat, lng);

        //Reverse Geocode here
        geocoder.geocode({'location': {lat, lng}}, function(results, status) {
            if (status === window.google.maps.GeocoderStatus.OK) {
                if (results[0]) {
                    // You will get the formatted address here, you can set it in your state or do whatever you want
                    console.log(results[0].formatted_address);
                } else {
                }
            } else {
            }
        });
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