import React, {useEffect, useState} from 'react';
import {useDispatch, useSelector} from 'react-redux';

import { gethangevents } from '../../../actions/hang';

import Hang from './Hang/Hang';
import {Box, Button, Grid, Paper} from "@mui/material";
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
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
            console.log(room);
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

    const back = () => {
        setCurrentHang("");
    }

    return(
        <Box sx={{display: "flex", width: "100%", height: "100%", justifyContent: "center", alignItems:"center"}}>
            <Paper elevation={16} sx={{display: "flex", width: '98%', height: "96%", borderRadius: "10px", alignItems: "center", justifyContent:"center"}}>
                {
                    currentHang === "" && (
                        <Box sx={{display: "flex", flexDirection: "column", width: "100%", height: "100%"}}>
                            <Box sx={{display: "flex", flexDirection: "row", width: "100%", height: "10%", justifyContent: "center", alignItems: "center"}}>
                                <h1 style={{margin: "0"}}>Your Hangs</h1>
                            </Box>
                            <Box sx={{width: "100%", height: "90%", display: "flex", justifyContent: "center", alignItems: "center"}}>
                                <Grid sx={{display: "flex", width: "100%", height: "100%", overflowY: "scroll"}} container spacing={2}>
                                    {hangs.map((hang) => (
                                        <Grid item xs={4} sx={{height: "50%"}}>
                                            <Hang key={hang.id} hang={hang} setCurrentHang={setCurrentHang}/>
                                        </Grid>
                                    ))}
                                </Grid>
                            </Box>
                        </Box>

                    )
                }
                {
                    currentHang !== "" && (
                        <Box sx={{display: "flex", width: "100%", height: "100%", flexDirection: "column"}}>
                            <Box sx={{display: "flex", flexDirection: "row", width: "100%", height: "7%", bgcolor: "#0c7c59", borderRadius: "10px 10px 0 0"}}>
                                <Box sx={{display: "flex", width: "50%", height: "100%"}}>
                                    <Button disableRipple sx={{color: "white", ":hover": {color: "black"}}}>
                                        <ArrowBackIcon onClick={back}/>
                                    </Button>
                                </Box>
                                <Box sx={{width: "50%", height: "100%", display: "flex", justifyContent: "flex-end"}}>
                                    <Button disableRipple sx={{color: "white", ":hover": {color: "black"}}}>
                                        Edit
                                    </Button>
                                </Box>
                            </Box>
                            <Box sx={{display: "block", width: "100%", height: "93%", flexDirection: "column", overflowY: "scroll"}}>
                                <Details currentHang={currentHang}/>
                            </Box>
                        </Box>
                    )
                }
            </Paper>
        </Box>

    )
}

export default Hangs;