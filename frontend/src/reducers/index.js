import { combineReducers } from 'redux';

import login from './login';
import chat from './chat';
import websocket from './websocket';

export const reducers = combineReducers({
    login,
    chat,
    websocket,
});