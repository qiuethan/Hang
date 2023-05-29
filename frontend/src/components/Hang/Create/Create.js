import React, { useEffect, useState } from 'react';
import { useDispatch } from 'react-redux'
import {useNavigate} from "react-router-dom";

import Name from './Fields/Name';
import Description from './Fields/Description';
import Picture from './Fields/Picture/Picture';
import Time from './Fields/Time';
import Location from './Fields/Location';
import Attendees from './Fields/Attendees';
import Needs from "./Fields/Needs/Needs";
import Tasks from "./Fields/Tasks/Tasks";

import logo from "../../../images/logo.svg";

import { createhangevent } from '../../../actions/hang';

import {Box, Paper, Stepper, Step, Button, TextField} from '@mui/material';


const Create = () => {

    const [user, setUser] = useState(JSON.parse(localStorage.getItem("profile")));

    const [fields, setFields] = useState({name: `${user.user.username}'s Hang`, description: `A Hang hosted by ${user.user.username}!`, picture: logo, owner: user.user.id, scheduled_time_start: "", scheduled_time_end: "", address: "", latitude: 0, longitude: 0, budget: 0.00, attendees: [user.user.id], needs: [], tasks: []});

    const [attendees, setAttendees] = useState([user]);
    const [needs, setNeeds] = useState([]);
    const [tasks, setTasks] = useState([]);

    const dispatch = useDispatch();
    const navigate = useNavigate();

    console.log(fields);

    useEffect(() => {
        setFields(fields);
    }, [fields])

    const handleChange = (event) => {
        event.preventDefault();
        setFields({...fields, [event.target.name]: event.target.value})
    }

    const updatePicture = (picture) => {
        setFields({...fields, picture: picture});
    }

    const updateLocation = (latitude, longitude) => {
        setFields({...fields, latitude: latitude, longitude: longitude})
    }

    const updateAttendee = (attendee) => {
        setAttendees([...attendees, attendee]);
        fields.attendees.push(attendee.user.id);
        console.log(attendees);
    }

    const handleBudget = (e) => {
        e.preventDefault();
        const budget = e.target.value;

            // Use regex to check if input is a float with two decimal places
        if (/^\d+(\.\d{0,2})?$/.test(budget)) {
            setFields({...fields, budget: budget});
        }
        if(budget === 0){
            setFields({...fields, budget: 0});
        }
    }

    const addNeed = (need) => {
        setNeeds([...needs, need]);
        fields.needs = [...fields.needs, need.need];
    }

    const deleteNeed = (n) => {
        setNeeds(needs.filter(need => need.n !== n));
        fields.needs = fields.needs.filter(need => need.n !== n).map( need => need.need);
    }

    const addTask = (task) => {
        setTasks([...tasks, task]);
        fields.tasks = [...fields.tasks, task.task]
    }

    const deleteTask = (n) => {
        setTasks(tasks.filter(task => task.n !== n));
        fields.tasks = fields.tasks.filter(task => task.n !== n).map(task => task.task);
    }
    const handleSubmit = (event) => {
        event.preventDefault();
        console.log(fields);
        dispatch(createhangevent(fields));
        navigate("/hang/")
    }


    const [step, setStep] = useState(0);

    const back = () => {
        setStep(step - 1);
    }

    const next = () => {
        setStep(step+1);
    }

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
                                        <Button sx={{backgroundColor: "#0c7c59", height: "80%", color: "white", ":hover": {color: "#0c7c59", backgroundColor: "white"}}} onClick={next}>Next</Button>
                                    </Box>
                                </Box>
                        </Box>
                    )}
                    {step === 3 && (
                        <Box sx={{position: "relative", width: "97%", height: "95%"}}>
                            <Box sx={{width: "100%", height: "100%"}}>
                                <Box sx={{display: "flex", width: "100%", height: "90%"}}>
                                    <Box sx={{display: "block", width: "50%", height:"100%", marginRight: "10px"}}>
                                        <Needs addNeed={addNeed} needs={needs} deleteNeed={deleteNeed}/>
                                    </Box>
                                    <Box sx={{display: "block", width: "50%", height:"100%", marginLeft: "10px"}}>
                                        <Tasks addTask={addTask} tasks={tasks} attendees={attendees} deleteTask={deleteTask}/>
                                    </Box>
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
                        </Box>
                    )}
            </Paper>
        </Box>
    )
}

export default Create;