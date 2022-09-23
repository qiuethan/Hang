import React from "react";

const Name = ({value, handleChange}) => {
    return (
        <div>
            <input
                type="text"
                name="name"
                value={value || ""}
                onChange={handleChange}
            />
        </div>
    )
}

export default Name;