import { combineReducers } from 'redux';

import login from './login';
import dms from './dms';
import groups from './groups';
import friends from './friends';
import websocket from './websocket';
import friendrequests from './friendrequests';
import hangs from './hangs'
import blocked from './blocked';
import users from './users';

export const reducers = combineReducers({
    login,
    dms,
    groups,
    friends,
    websocket,
    friendrequests,
    hangs,
    blocked,
    users,
});