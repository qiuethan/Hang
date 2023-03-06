import { useRef, useEffect } from "react";

const Autocomplete = ({inputRef}) => {
    const autoCompleteRef = useRef();

    const options = {
        fields: ["address_components", "geometry", "icon", "name"]
    };

    useEffect(() => {
        autoCompleteRef.current = new window.google.maps.places.Autocomplete(
            inputRef.current,
            options
        )
    }, []);

    return(
        <div/>
    );
};

export default Autocomplete;