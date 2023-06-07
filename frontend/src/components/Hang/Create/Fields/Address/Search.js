/*
Author: Ethan Qiu
Filename: Search.js
Last Modified: June 7, 2023
Description: Allows user to search address
*/

import React, {useRef} from 'react';

import Autocomplete from "./Autocomplete";
import {Box} from "@mui/material";

//Search parameter
const Search = ({updateLocation, fields, setFields}) => {

    //Input reference
    const inputRef = useRef();

    //Create geocoder object
    const geocoder = new window.google.maps.Geocoder();

    //Handle change in search bar
    const handleChange = (e) => {
        e.preventDefault();
        //Update fields
        setFields({...fields, address: e.target.value});
    }

    //When sbmit
    const geocodeAddress = (e) => {
        e.preventDefault();
        //Use geocode + address to find latitude and longitude of location
        geocoder.geocode({ 'address': e.target.elements.address.value }, function handleResults (results, status){
                //If address found
                if(status === window.google.maps.GeocoderStatus.OK){
                    //update fields
                    setFields({...fields, address: e.target.elements.address.value, latitude: results[0].geometry.location.lat(), longitude: results[0].geometry.location.lng()});
                }
            }
        );
    }

    //Render component
    return(
        <Box sx={{display: "flex", marginBottom: "10px", width: "100%", justifyContent:"center"}}>
            <form onSubmit={geocodeAddress} style={{display: "flex", flexDirection: "row", width: "70%"}}>
                <label style={{marginRight: "5px"}}>Enter Address:</label>
                <input name="address" ref={inputRef} value={fields.address} onChange={handleChange} style={{width: "70%"}}/>
                <button type="submit" style={{marginLeft: "5px"}}>Submit</button>
            </form>
            <Autocomplete inputRef={inputRef} fields={fields} setFields={setFields}/>
        </Box>
    );
};

export default Search;