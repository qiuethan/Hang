/*
Author: Ethan Qiu
Filename: actionTypes.js
Last Modified: June 7, 2023
Description: Store standardized actionType constants
*/

//Authentication
export const LOGIN = 'LOGIN';
export const LOGOUT = 'LOGOUT';

//Users
export const GETSELF = 'GETSELF';
export const GETUSER = 'GETUSER';

//Chat Rooms
export const LOADROOMS = 'LOADROOMS';
export const LOADGROUPS = 'LOADGROUPS';

//Webscokets
export const CONNECTWS = 'CONNECTWS';
export const CONNECTRTWS = 'CONNECTRTWS';

//Friends
export const LOADFRIENDS = 'LOADFRIENDS';
export const LOADRECEIVEDFRIENDREQUESTS = 'LOADRECEIVEDFRIENDREQUESTS';
export const ACCEPTFRIENDREQUEST = 'ACCEPTFRIENDREQUEST';
export const DECLINEFRIENDREQUEST = 'DECLINEFRIENDREQUEST'
export const REMOVEFRIEND = 'REMOVEFRIEND';
export const BLOCKFRIEND = 'BLOCKFRIEND';
export const LOADBLOCKEDUSERS = 'LOADBLOCKEDUSERS';
export const DELETESENTFRIENDREQUEST = 'DELETESENTFRIENDREQUEST';
export const LOADSENTFRIENDREQUESTS = 'LOADSENTFRIENDREQUESTS';
export const UNBLOCKUSER = 'UNBLOCKUSER';

//Hang Evemts
export const CREATEHANGEVENT = 'CREATEHANGEVENT';
export const GETHANGEVENTS = 'GETHANGEVENTS';

//Notifications
export const GETUNREADNOTIFICATIONS = 'GETUNREADNOTIFICATIONS';

//URLs
export const BASEURL = "https://hang-backend.fly.dev/";
export const BASEWS = "wss://hang-backend.fly.dev/";
export const FRONTENDURL = "https://hang-coherentboi.vercel.app/";
