import { combineReducers } from 'redux';

import login from './login';
import chat from './chat';

export const reducers = combineReducers({
    login,
    chat,
});