import axios from 'axios';

//API Setup
const API = axios.create({ baseURL: 'https://hang-backend.fly.dev/' });

API.interceptors.request.use((req) => {
    if (localStorage.getItem('profile')){
        req.headers.Authorization = `Token ${JSON.parse(localStorage.getItem('profile')).token}`;
    }

    return req;
});


//Authentication
export const login = (inputs) => API.post('/v1/accounts/login/', inputs);
export const signin = (inputs) => API.post('/v1/accounts/register/', inputs);
export const logout = (token) => API.post('/v1/accounts/logout/', null);
export const sendemail = (inputs) => API.post('/v1/accounts/email_verification_tokens/', inputs);
export const googlelogin = (code) => API.post('/v1/accounts/login/google/', {code: code});

//Load Rooms List
export const loadrooms = () => API.get('/v1/chats/direct_messages/');
export const loadgroups = () => API.get('/v1/chats/group_chats/');

//Users
export const getuser = (id) => API.get(`/v1/accounts/users/id/${id}/`);
export const getuserbyusername = (username) => API.get(`/v1/accounts/users/username/${username}/`)
export const getuserbyemail = (email) => API.get(`/v1/accounts/users/email/${email}/`)
export const getcurrentuser = () => API.get('/v1/accounts/users/me/');
export const updatepicture = (picture) => API.patch('/v1/accounts/users/me/', {profile_picture: picture})
export const updateaboutme = (aboutMe) => API.patch('/v1/accounts/users/me/', {about_me: aboutMe});

//Friends
export const loadfriends = () => API.get('/v1/accounts/friends/');
export const removefriend = (id) => API.delete(`/v1/accounts/friends/${id}/`);
export const blockfriend = (id) => API.post(`v1/accounts/blocked_users/`, {id: id});
export const loadblockedusers = () => API.get('/v1/accounts/blocked_users/');
export const unblockuser = (id) => API.delete(`/v1/accounts/blocked_users/${id}/`);

//Friend Requests
export const loadrecievedfriendrequests = () => API.get('/v1/accounts/friend_requests/received/');
export const acceptfriendrequest = (id) => API.delete(`/v1/accounts/friend_requests/received/${id}/`);
export const declinefriendrequest = (id) => API.patch(`/v1/accounts/friend_requests/received/${id}/`);
export const sendfriendrequest = (id) => API.post(`/v1/accounts/friend_requests/sent/`, {to_user: id});
export const loadsentfriendrequests = () => API.get('/v1/accounts/friend_requests/sent/');
export const deletesentfriendrequest = (id) => API.delete(`/v1/accounts/friend_requests/sent/${id}/`);

//Hang Requests
export const createhangevent = (inputs) => {console.log(inputs); API.post('/v1/hang_events/unarchived/', inputs)};
export const gethangevents = () => API.get('/v1/hang_events/unarchived/');
export const joinhangevent = (code) => API.post('/v1/hang_events/invitation_codes/join/', {invitation_code: code})

//Notifications
export const getunreadnotifications = () => API.get('/v1/notifications/notifications/unread/');
