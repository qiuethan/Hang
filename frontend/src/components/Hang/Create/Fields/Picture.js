import React from "react";

const Picture = ({value, handleChange}) => {
    return (
        <div>
            <input
                type="text"
                name="picture"
                value={value || ""}
                onChange={handleChange}
            />
        </div>
    )
}

export default Picture;
