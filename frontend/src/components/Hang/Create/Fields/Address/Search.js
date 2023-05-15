import React, {useState, useRef} from 'react';

import Autocomplete from "./Autocomplete";
import {Box} from "@mui/material";

const Search = ({updateLocation}) => {

    const inputRef = useRef();

    const [address, setAddress] = useState("");

    const geocoder = new window.google.maps.Geocoder();

    const handleChange = (e) => {
        e.preventDefault();
        setAddress(e.target.value);
    }

    const geocodeAddress = (e) => {
        e.preventDefault();
        geocoder.geocode({ 'address': address }, function handleResults (results, status){

            if(status === window.google.maps.GeocoderStatus.OK){

                updateLocation(results[0].geometry.location.lat(), results[0].geometry.location.lng());

                setAddress("");

                return;
            }

            }
        );
    }

    return(
        <Box sx={{display: "flex", marginBottom: "10px", width: "100%", justifyContent:"center"}}>
            <form onSubmit={geocodeAddress} style={{display: "flex", flexDirection: "row", width: "70%"}}>
                <label style={{marginRight: "5px"}}>Enter Address:</label>
                <input ref={inputRef} value={address} onChange={handleChange} style={{width: "70%"}}/>
                <button type="submit" style={{marginLeft: "5px"}}>Submit</button>
            </form>
            <Autocomplete inputRef={inputRef} setAddress={setAddress}/>
        </Box>
    );
};

export default Search;