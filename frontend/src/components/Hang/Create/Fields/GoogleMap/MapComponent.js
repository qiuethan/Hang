/*
Author: Ethan Qiu
Filename: MapComponent.js
Last Modified: June 7, 2023
Description: Renders interactive google map for user
*/

import React, {useEffect, useState} from "react";
import { GoogleMap, LoadScript, Marker } from '@react-google-maps/api';

//Set styles for container
const containerStyle = {
    width: '95%',
    height: '98%'
};

//MapComponent Component
const MapComponent = ({updateLocation, fields, setFields }) => {

    //When clicked
    const handleClick = (e) => {
        //Create new geocoder object
        const geocoder = new window.google.maps.Geocoder();

        //Save latitude and longitude
        const lat = e.latLng.lat();
        const lng = e.latLng.lng();

        //Update location to new latitude and longitude
        updateLocation(lat, lng);

        //Reverse Geocode here
        geocoder.geocode({'location': {lat, lng}}, function(results, status) {
            //If found
            if (status === window.google.maps.GeocoderStatus.OK) {
                if (results[0]) {
                    // If result found, set address to new formatted address
                    setFields({...fields, address: results[0].formatted_address, longitude: lng, latitude: lat})
                } else {

                }
            } else {
                //Not found, set address to none
                setFields({...fields, address: "None"})
            }
        });
    };

    //Render Component
    return(
        <GoogleMap
                mapContainerStyle={containerStyle}
                center={{lat: +fields.latitude, lng: +fields.longitude}}
                zoom={16}
                onClick={handleClick}
            >
                <Marker position={{lat: +fields.latitude, lng: +fields.longitude}}/>
        </GoogleMap>

    );
}

export default MapComponent;