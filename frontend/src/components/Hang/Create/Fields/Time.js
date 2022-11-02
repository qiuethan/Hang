import React from "react";

const Time = ({start, end, handleChange}) => {
    return(
        <div>
            <input
                type="text"
                name="scheduled_time_start"
                value={start || ""}
                onChange={handleChange}
            />
            <input
                type="text"
                name="scheduled_time_end"
                value={end || ""}
                onChange={handleChange}
            />
        </div>
    )
}

export default Time