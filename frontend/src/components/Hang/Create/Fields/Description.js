import React from "react";

const Description = ({value, handleChange}) => {
    return (
        <div>
            <input
                type="text"
                name="description"
                value={value || ""}
                onChange={handleChange}
            />
        </div>
    )
}

export default Description;