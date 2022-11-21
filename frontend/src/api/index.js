import axios from 'axios';

//API Setup
const API = axios.create({ baseURL: 'http://localhost:8000' });

API.interceptors.request.use((req) => {
    if (localStorage.getItem('profile')){
        req.headers.Authorization = `Token ${JSON.parse(localStorage.getItem('profile')).token}`;
    }

    return req;
});


//Authentication
export const login = (inputs) => API.post('/v1/accounts/login', inputs);
export const signin = (inputs) => API.post('/v1/accounts/register', inputs);
export const logout = (token) => API.post('/v1/accounts/logout', null);
export const sendemail = (inputs) => API.post('/v1/accounts/send_email', inputs);

//Load Rooms List
export const loadrooms = () => API.get('/v1/chat/direct_message');
export const loadgroups = () => API.get('/v1/chat/group_chat');

//Users
export const getuser = (id) => API.get(`/v1/accounts/user/${id}`);

//Friends
export const loadfriends = () => API.get('/v1/accounts/friends');
export const removefriend = (id) => API.delete(`/v1/accounts/friends/${id}`)
export const blockfriend = (id) => API.post(`v1/accounts/blocked_users`, {id: id})

//Friend Requests
export const loadrecievedfriendrequests = () => API.get('/v1/accounts/received_friend_request');
export const acceptfriendrequest = (id) => API.delete(`/v1/accounts/received_friend_request/${id}`);
export const declinefriendrequest = (id) => API.patch(`/v1/accounts/received_friend_request/${id}`);
export const sendfriendrequest = (email) => API.post(`/v1/accounts/sent_friend_request`, {to_user: { email: email }})
 
//Hang Requests
export const createhangevent = (inputs) => API.post('/v1/hang_event/hang_event', inputs);