import React, {useState, useRef} from 'react';

import Autocomplete from "./Autocomplete";
import {Box} from "@mui/material";

const Search = ({updateLocation, fields, setFields}) => {

    const inputRef = useRef();

    const geocoder = new window.google.maps.Geocoder();

    const handleChange = (e) => {
        e.preventDefault();
        setFields({...fields, address: e.target.value});
        console.log(fields.address);
    }

    const geocodeAddress = (e) => {
        e.preventDefault();
        console.log(e);
        console.log(e.target.elements.address.value);
        geocoder.geocode({ 'address': e.target.elements.address.value }, function handleResults (results, status){
                console.log(fields.address);
                console.log(status);
                if(status === window.google.maps.GeocoderStatus.OK){
                    console.log("check");
                    setFields({...fields, address: e.target.elements.address.value, latitude: results[0].geometry.location.lat(), longitude: results[0].geometry.location.lng()});
                }
            }
        );
    }

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