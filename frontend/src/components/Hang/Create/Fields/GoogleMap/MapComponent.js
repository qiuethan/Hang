import React, {useEffect, useState} from "react";

import { GoogleMap, LoadScript, Marker } from '@react-google-maps/api';

const containerStyle = {
    width: '95%',
    height: '98%'
};

const MapComponent = ({updateLocation, fields, setFields }) => {

    const handleClick = (e) => {
        const geocoder = new window.google.maps.Geocoder();

        const lat = e.latLng.lat();
        const lng = e.latLng.lng();
        console.log(lat, lng);
        updateLocation(lat, lng);

        //Reverse Geocode here
        geocoder.geocode({'location': {lat, lng}}, function(results, status) {
            if (status === window.google.maps.GeocoderStatus.OK) {
                if (results[0]) {
                    // You will get the formatted address here, you can set it in your state or do whatever you want
                    console.log(results[0].formatted_address);
                    setFields({...fields, address: results[0].formatted_address, longitude: lng, latitude: lat})
                } else {

                }
            } else {
                setFields({...fields, address: "None"})
            }
        });
    };

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