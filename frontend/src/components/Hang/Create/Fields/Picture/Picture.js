import React, { useState } from "react";
import {Box} from "@mui/material";

import './Picture.css';
const Picture = ({picture, updatePicture}) => {

    const handleImageChange = (e) => {
        const selectedImage = e.target.files[0];
        const reader = new FileReader();
        console.log(reader);
        reader.readAsDataURL(selectedImage);
        reader.onload = () => {
            updatePicture(reader.result);
            console.log(picture);
        };
    }

    return (
        <Box sx={{position: "relative", width:"100%", height: "100%", overflow:"hidden"}}>
                <label htmlFor="image-input">
                    <Box id="image" sx={{display: "flex", width: "100%", height: "100%", alignItems:"center", justifyContent:"center"}}>
                        {picture && <img style={{display: "block", justifySelf: "center", alignSelf: "center", maxWidth: "95%", maxHeight: "95%", objectFit: "cover", borderRadius: "10px"}} className="image-preview" src={picture} alt="Uploaded Image"/>}
                        <div className="overlay">
                            Click To Choose Image
                        </div>
                    </Box>
                </label>
                <input
                    type="file"
                    id="image-input"
                    accept="image/*"
                    name="picture"
                    onChange={handleImageChange}
                    style={{display: "none"}}
                />
        </Box>
    )
}

export default Picture;
