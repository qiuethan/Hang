import { w3cwebsocket as W3CWebSocket } from "websocket";

export const client = JSON.parse(localStorage.getItem('profile')) !== null ? new W3CWebSocket(`ws://localhost:8000/ws/chat/${JSON.parse(localStorage.getItem('profile')).user.username}/`) : null;