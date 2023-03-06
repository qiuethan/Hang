import React, {useState} from "react";

import Search from "./Address/Search";
import MapComponent from "./GoogleMap/MapComponent";

const Location = ({longitude, latitude, updateLocation}) => {

    const [address, setAddress] = useState("");

    const changeAddress = (e) => {
        e.preventDefault();
        setAddress(e.target.value);
    }

    return(
        <div>
            <Search updateLocation={updateLocation}/>
            <MapComponent latitude={latitude} longitude={longitude} updateLocation={updateLocation}/>
        </div>
    )
}

export default Location;