import React, { useEffect } from 'react';
import {useDispatch, useSelector} from 'react-redux';

import { gethangevents } from '../../../actions/hang';

import Hang from './Hang/Hang';
import {Box, Button, Grid} from "@mui/material";

const Hangs = () => {

    const dispatch = useDispatch();

    const hangs = useSelector((state) => state.hangs);
    console.log(hangs);

    useEffect(() => {
        dispatch(gethangevents());
    }, [])

    return(
        <Box sx={{display: "flex", width: "100%", height: "100%", justifyContent: "center", alignItems:"center", overflowY: "scroll"}}>
            <Box sx={{display: "flex", width: '98%', height: "95%"}}>
                <Grid sx={{display: "flex", width: "100%", height: "100%"}} container spacing={2}>
                    {hangs.map((hang) => (
                        <Grid item xs={4} sx={{height: "50%"}}>
                            <Hang key={hang.id} hang={hang}/>
                        </Grid>
                    ))}
                </Grid>
            </Box>
        </Box>

    )
}

export default Hangs;