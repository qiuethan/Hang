import { useRef, useEffect } from "react";

const Autocomplete = ({inputRef, setAddress}) => {
    const autoCompleteRef = useRef();

    const options = {
        fields: ["address_components", "geometry", "icon", "name"]
    };

    useEffect(() => {
        autoCompleteRef.current = new window.google.maps.places.Autocomplete(
            inputRef.current,
            options
        );

        // Listen for the 'place_changed' event
        autoCompleteRef.current.addListener("place_changed", () => {
            const selectedPlace = autoCompleteRef.current.getPlace();
            setAddress(selectedPlace.address_components.map(address => address.short_name).join(" ")); // Log the selected place object
        });
    }, []);

    return(
        <div/>
    );
};

export default Autocomplete;