// for test purposes only
let token ='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjg1Mjc3NTk0LCJpYXQiOjE2ODI2ODU1OTQsImp0aSI6IjFkY2YzZGYwZDVkYTQ3N2JiMjg1OTMzZWE0MTFkMWQ4IiwidXNlcl9pZCI6MX0.GsIQWm-uihebC_gGObguPGkCgqFSXmtK1kIm4P_xjjE'
// let endpoint = "ws://localhost:8000/machines/recycle/start/machine/"
// let endpoint = "wss://dropme.onrender.com/machines/recycle/start/machine/"
let endpoint = "ws://localhost:8000/ws/chat/room1/"
const ws = new WebSocket(endpoint + "?token=" + token)

ws.addEventListener('message', (event) => {
    console.log('Message from server ', event.data);
});

ws.addEventListener('close', (event) => {
    console.log('The connection has been closed successfully.');
});



