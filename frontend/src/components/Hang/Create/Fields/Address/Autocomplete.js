/*
Author: Ethan Qiu
Filename: Autocomplete.js
Last Modified: June 7, 2023
Description: Creates autocomplete for user
*/

import { useRef, useEffect } from "react";

const Autocomplete = ({inputRef, fields, setFields}) => {
    const autoCompleteRef = useRef();

    const options = {
        fields: ["address_components", "geometry", "formatted_address", "icon", "name"]
    };

    useEffect(() => {
        autoCompleteRef.current = new window.google.maps.places.Autocomplete(
            inputRef.current,
            options
        );

        // Listen for the 'place_changed' event
        autoCompleteRef.current.addListener("place_changed", () => {
            const selectedPlace = autoCompleteRef.current.getPlace().name;
            console.log(selectedPlace);
            setFields({...fields, address: selectedPlace.formatted_address}); // Log the selected place object
        });
    }, []);

    return(
        <div/>
    );
};

export default Autocomplete;