import axios from 'axios';

const API = axios.create({ baseURL: 'http://localhost:8000'});

API.interceptors.request.use((req) => {
    if(localStorage.getItem('profile')){
        req.headers.Authorization = `Bearer ${JSON.parse(localStorage.getItem('profile')).token}`;
    }

    return req;
});

export const login = (inputs) => API.post('/dj-rest-auth/login/', inputs);
export const signin = (inputs) => API.post('/dj-rest-auth/registration/', inputs);