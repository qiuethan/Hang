/*
Author: Ethan Qiu
Filename: Create.js
Last Modified: June 7, 2023
Description: Allows users to create hangs
*/

import React, { useEffect, useState } from 'react';
import {useDispatch, useSelector} from 'react-redux'
import {useNavigate} from "react-router-dom";

import Name from './Fields/Name';
import Description from './Fields/Description';
import Picture from './Fields/Picture/Picture';
import Time from './Fields/Time';
import Location from './Fields/Location';
import Attendees from './Fields/Attendees';

import logo from "../../../images/logo.svg";

import {addtocalendar, createhangevent, generatejoinlink} from '../../../actions/hang';

import {Box, Paper, Button} from '@mui/material';
import {createdm, loadrooms} from "../../../actions/chat";
import {FRONTENDURL} from "../../../constants/actionTypes";

//Create component
const Create = () => {

    //Create user state variable
    const [user, setUser] = useState(JSON.parse(localStorage.getItem("profile")));

    //Create fields state variable
    const [fields, setFields] = useState({name: `${user.user.username}'s Hang`, description: `A Hang hosted by ${user.user.username}!`, picture: logo, owner: user.user.id, scheduled_time_start: "", scheduled_time_end: "", address: "", latitude: 0, longitude: 0, budget: 0.00, attendees: [user.user.id], needs: [], tasks: []});

    //Create attendees state variable
    const [attendees, setAttendees] = useState([user]);

    //Define dispatch + navigate
    const dispatch = useDispatch();
    const navigate = useNavigate();

    //Get client from react store
    const client = useSelector((state) => state.websocket);

    //Get rooms from react store
    const rooms = useSelector((state) => state.dms);

    //On render + fields change
    useEffect(() => {
        //Update fields live
        setFields(fields);
    }, [fields])

    //On render
    useEffect(() => {
        //Load dm rooms
        dispatch(loadrooms());
    }, [])

    //Handle changes made in components
    const handleChange = (event) => {
        event.preventDefault();
        setFields({...fields, [event.target.name]: event.target.value})
    }

    //Update picture in component
    const updatePicture = (picture) => {
        setFields({...fields, picture: picture});
    }

    //Update locaiton in component
    const updateLocation = (latitude, longitude) => {
        setFields({...fields, latitude: latitude, longitude: longitude})
    }

    //Update attendees in component
    const updateAttendee = (attendee) => {
        setAttendees([...attendees, attendee]);
        fields.attendees.push(attendee.user.id);
    }

    //Update budget in component
    const handleBudget = (e) => {
        e.preventDefault();
        const budget = e.target.value;

        //Check if input is a float with two decimal places
        if (/^\d+(\.\d{0,2})?$/.test(budget)) {
            setFields({...fields, budget: budget});
        }
        if(budget === 0){
            setFields({...fields, budget: 0});
        }
    }

    //Submit fields to backend API
    const handleSubmit = (event) => {
        event.preventDefault();
        //Create hang event and returns hang event values
        dispatch(createhangevent(fields)).then((r) => {
            //Adds hang event to calendar
            dispatch(addtocalendar(r.id)).then((s) => {
                //Generates join link for hang event and returns to component
                dispatch(generatejoinlink(r.id)).then((join) => {
                    //For each attendee besides self
                    attendees.slice(1, attendees.length).forEach((attendee) => {
                        //Find dm room with attendee
                        const findDm = rooms.filter((room) => room.users.includes(attendee.user.id))
                        //If found
                        if(findDm.length > 0){
                            //Send join link
                            client.send(JSON.stringify({
                                action: "send_message",
                                content: {
                                    message_channel: findDm[0].id,
                                    content: `${FRONTENDURL}hang/join?code=${join.invitation_code}`,
                                    reply: null
                                }
                            }));
                        }
                        else{
                            //Create dm with attendee
                            dispatch(createdm(attendee.id)).then((code) =>{
                                //Send join link
                                client.send(JSON.stringify({
                                    action: "send_message",
                                    content: {
                                        message_channel: code,
                                        content: `${FRONTENDURL}hang/join?code=${join.invitation_code}`,
                                        reply: null
                                    }
                                }));
                            })
                        }
                    });
                    //Navigate back to hang
                    navigate("/hang");
                })
            });
        });
    }

    //Step state variable
    const [step, setStep] = useState(0);

    //Go to previous page
    const back = () => {
        setStep(step - 1);
    }

    //Go to next page
    const next = () => {
        setStep(step+1);
    }

    //Render components
    return(
        <Box sx={{display: 'flex', alignItems: 'center', justifyContent: 'center', width: '100%', height: '100%'}}>
            <Paper elevation={16} sx={{display: "flex", width: "70%", height: "90%", borderRadius: "10px", justifyContent: "center", alignItems: "center"}}>
                    {step === 0 && (
                        <Box sx={{position: "relative", width: "97%", height: "95%"}}>
                                <Box sx={{display: "flex", width: "100%", height: "15%"}}>
                                    <Name value={fields.name} handleChange={handleChange}/>
                                </Box>
                                <Box sx={{display: "flex", flexDirection:"row", justifyContent: "center", width:"100%", height:"75%"}}>
                                    <Box sx={{width: "50%", height: "100%"}}>
                                        <Box sx={{display: "flex", height: "100%", width: "100%"}}>
                                            <Box sx={{width: "100%", height: "100%", marginRight: "5px", borderRadius: "10px", backgroundColor: "#a5d6b0"}}>
                                                <Box sx={{marginRight: "12px", marginLeft: "12px", marginBottom: "12px"}}>
                                                    <Description value={fields.description} handleChange={handleChange}/>
                                                </Box>
                                            </Box>
                                        </Box>
                                    </Box>
                                    <Box sx={{width: "50%", height: "100%"}}>
                                        <Box sx={{display: "flex", height: "100%", width: "100%"}}>
                                            <Box sx={{width: "100%", height: "100%", borderRadius: "10px", backgroundColor: "#a5d6b0", marginLeft: "5px"}}>
                                                <Picture picture={fields.picture} updatePicture={updatePicture}/>
                                            </Box>
                                        </Box>
                                    </Box>
                                </Box>
                                <Box sx={{display: "flex", width: "100%", height:"10%", alignSelf: "flex-end", alignItems: "flex-end"}}>
                                    <Box sx={{display: "flex", width: "100%", height: "100%", alignItems:"flex-end", justifyContent:"flex-end"}}>
                                        <Button sx={{backgroundColor: "#0c7c59", height: "80%", color: "white", ":hover": {color: "#0c7c59", backgroundColor: "white"}}} onClick={next}>Next</Button>
                                    </Box>
                                </Box>
                        </Box>
                    )}
                    {step === 1 && (
                        <Box sx={{position: "relative", width: "97%", height: "95%"}}>
                                <Box sx={{width: "100%", height: "100%"}}>
                                    <Box sx={{display: "flex", width: "100%", height: "90%"}}>
                                        <Box sx={{display: "flex", width: "50%"}}>
                                            <Time start={fields.scheduled_time_start} end={fields.scheduled_time_end} handleChange={handleChange}/>
                                        </Box>
                                        <Box sx={{display: "flex", flexDirection:"column", width: "50%"}}>
                                            <Attendees attendees={attendees} updateAttendee={updateAttendee} fields={fields}/>
                                            <Box sx={{display: "flex", flexDirection: "row", width: "100%", justifyContent: "center"}}>
                                                <h3>Budget</h3>
                                            </Box>
                                            <Box>
                                                <label htmlFor="budget" style={{marginRight: "2px"}}>$</label>
                                                <input id="budget" type="text" value={fields.budget}
                                                           onChange={handleBudget} style={{width: "97%"}}/>
                                            </Box>
                                        </Box>
                                    </Box>
                                    <Box sx={{display: "flex", width: "100%", height:"10%", alignSelf: "flex-end", alignItems: "flex-end"}}>
                                        <Box sx={{display: "flex", width: "50%", height: "100%", alignItems:"flex-end"}}>
                                            <Button sx={{backgroundColor: "#0c7c59", height: "80%", color: "white", ":hover": {color: "#0c7c59", backgroundColor: "white"}}} onClick={back}>Back</Button>
                                        </Box>
                                        <Box sx={{display: "flex", width: "50%", height: "100%", alignItems:"flex-end", justifyContent:"flex-end"}}>
                                            <Button sx={{backgroundColor: "#0c7c59", height: "80%", color: "white", ":hover": {color: "#0c7c59", backgroundColor: "white"}}} onClick={next}>Next</Button>
                                        </Box>
                                    </Box>
                                </Box>
                        </Box>
                    )}
                    {step === 2 && (
                        <Box sx={{position: "relative", width: "97%", height: "95%"}}>
                                <Box sx={{height: "90%", width: "100%"}}>
                                    <Location longitude={fields.longitude} latitude={fields.latitude} fields={fields} setFields={setFields} updateLocation={updateLocation}/>
                                </Box>
                                <Box sx={{display: "flex", width: "100%", height:"10%", alignSelf: "flex-end", alignItems: "flex-end"}}>
                                    <Box sx={{display: "flex", width: "50%", height: "100%", alignItems:"flex-end"}}>
                                        <Button sx={{backgroundColor: "#0c7c59", height: "80%", color: "white", ":hover": {color: "#0c7c59", backgroundColor: "white"}}} onClick={back}>Back</Button>
                                    </Box>
                                    <Box sx={{display: "flex", width: "50%", height: "100%", alignItems:"flex-end", justifyContent:"flex-end"}}>
                                        <Button sx={{backgroundColor: "#0c7c59", height: "80%", color: "white", ":hover": {color: "#0c7c59", backgroundColor: "white"}}} onClick={handleSubmit}>Submit</Button>
                                    </Box>
                                </Box>
                        </Box>
                    )}

            </Paper>
        </Box>
    )
}

export default Create;