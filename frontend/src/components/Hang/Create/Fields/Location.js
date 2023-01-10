import React, {useState} from "react";

import MapComponent from "./GoogleMap/MapComponent";

const Location = ({longitude, latitude, handleChange}) => {

    const [address, setAddress] = useState("");

    const changeAddress = (e) => {
        e.preventDefault();
        setAddress(e.target.value);
    }

    return(
        <div>
            <input
                type="text"
                name="address"
                value={address}
                onChange={changeAddress}
            />
            <input
                type="text"
                name="latitude"
                value={latitude.toString() || ""}
                onChange={handleChange}
            />
            <input
                type="text"
                name="longitude"
                value={longitude.toString() || ""}
                onChange={handleChange}
            />
            <MapComponent latitude={latitude} longitude={longitude}/>
        </div>
    )
}

export default Location;