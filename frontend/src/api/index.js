import axios from 'axios';

const API = axios.create({ baseURL: 'http://localhost:8000' });

API.interceptors.request.use((req) => {
    if (localStorage.getItem('profile')){
        req.headers.Authorization = `Token ${JSON.parse(localStorage.getItem('profile')).token}`;
    }

    return req;
});

export const login = (inputs) => API.post('/v1/accounts/login', inputs);
export const signin = (inputs) => API.post('/v1/accounts/register', inputs);
export const logout = (token) => API.post('/v1/accounts/logout', null);

export const sendemail = (inputs) => API.post('/v1/accounts/send_email', inputs);

//Load Rooms List
export const loadrooms = () => API.get('/v1/chat/direct_message');
export const loadgroups = () => API.get('/v1/chat/group_chat');

//Load Friends

export const loadfriends = () => API.get('/v1/accounts/friends');