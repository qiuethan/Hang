import React, {useEffect, useState} from 'react';
import {useDispatch, useSelector} from 'react-redux';

import { gethangevents } from '../../../actions/hang';

import Hang from './Hang/Hang';
import {Box, Button, Grid, Paper} from "@mui/material";
import Details from "./Details/Details";
import {useSearchParams} from "react-router-dom";

const Hangs = () => {

    const dispatch = useDispatch();

    const hangs = useSelector((state) => state.hangs);
    console.log(hangs);

    useEffect(() => {
        dispatch(gethangevents());
    }, [])

    useEffect(() => {
        if(hangs.length !== 0){
            const room = getRoom();
            if(room !== null){
                setCurrentHang(+room);
            }
            else{
                setCurrentHang("");
            }
        }
    }, [hangs])

    const [currentHang, setCurrentHang] = useState("");
    const [searchParams, setSearchParams] = useSearchParams();

    const getRoom = () => {
        return searchParams.get("room");
    }


    return(
        <Box sx={{display: "flex", width: "100%", height: "100%", justifyContent: "center", alignItems:"center"}}>
            <Paper elevation={16} sx={{display: "flex", width: '98%', height: "96%", borderRadius: "10px", alignItems: "center", justifyContent:"center"}}>
                {
                    currentHang === "" && (
                        <Grid sx={{display: "flex", width: "100%", height: "100%", overflowY: "scroll"}} container spacing={2}>
                            {hangs.map((hang) => (
                                <Grid item xs={4} sx={{height: "50%"}}>
                                    <Hang key={hang.id} hang={hang} setCurrentHang={setCurrentHang}/>
                                </Grid>
                            ))}
                        </Grid>
                    )
                }
                {
                    currentHang !== "" && (
                        <Details currentHang={currentHang}/>
                    )
                }
            </Paper>
        </Box>

    )
}

export default Hangs;