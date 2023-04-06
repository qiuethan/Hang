import { combineReducers } from 'redux';

import login from './login';
import dms from './dms';
import groups from './groups';
import friends from './friends';
import websocket from './websocket';
import rtws from './rtws';
import friendrequests from './friendrequests';
import sentrequests from "./sentrequests";
import notifications from './notifications'
import hangs from './hangs'
import blocked from './blocked';
import users from './users';
import profile from "./profile";

export const reducers = combineReducers({
    login,
    dms,
    groups,
    friends,
    websocket,
    friendrequests,
    sentrequests,
    hangs,
    blocked,
    users,
    notifications,
    profile,
    rtws,
});
