import React, {useState, useRef} from 'react';

import Autocomplete from "./Autocomplete";

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
        <div>
            <form onSubmit={geocodeAddress}>
                <label>Enter Address: </label>
                <input ref={inputRef} value={address} onChange={handleChange}/>
                <button type="submit">Submit</button>
            </form>
            <Autocomplete inputRef={inputRef}/>
        </div>
    );
};

export default Search;