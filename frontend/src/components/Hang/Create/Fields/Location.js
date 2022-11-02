import React from "react";

const Location = ({longitude, latitude, handleChange}) => {
    return(
        <div>
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
        </div>
    )
}

export default Location;