import { combineReducers } from 'redux';

import login from './login';
import dms from './dms';
import groups from './groups';
import websocket from './websocket';

export const reducers = combineReducers({
    login,
    dms,
    groups,
    websocket,
});