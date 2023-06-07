/*
Author: Ethan Qiu
Filename: index.js
Last Modified: June 7, 2023
Description: Core renderer of application
*/


import React from 'react';
import ReactDOM from 'react-dom/client';
import { Provider } from 'react-redux';
import { createStore, applyMiddleware, compose } from 'redux';
import thunk from 'redux-thunk';

import App from './App';
import {reducers} from './reducers';

//Create redux store
const store = createStore(reducers, compose(applyMiddleware(thunk)));

//Create application root
const root = ReactDOM.createRoot(document.getElementById('root'));

//Render appliccation
root.render(
  <Provider store = {store}>
    <App />
  </Provider>
);