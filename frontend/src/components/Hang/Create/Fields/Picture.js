import React, { useState } from "react";

const Picture = ({picture, updatePicture}) => {

    const handleImageChange = (e) => {
        const selectedImage = e.target.files[0];
        updatePicture(URL.createObjectURL(selectedImage));
        console.log(picture);
    }

    return (
        <div>
            <input
                type="file"
                accept="image/*"
                name="picture"
                onChange={handleImageChange}
            />
            {picture && <img src={picture} alt="Uploaded Image"/>}
        </div>
    )
}

export default Picture;
