// for test purposes only
let token ='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjg2MTM5NDkzLCJpYXQiOjE2ODM1NDc0OTMsImp0aSI6ImU0NjBmOWY0YWM2MTRjZTM4NjlmODQ0NWM4MWU3YzM3IiwidXNlcl9pZCI6MX0.Y8y_9h_a5NZ-OCFmv1SM9a_vltTuH4RVdWPGT4xri2M'
// let endpoint = "ws://localhost:8000/machines/recycle/start/machine/"
// let endpoint = "wss://dropme.onrender.com/machines/recycle/start/machine/"
let endpoint = "wss://dropme.up.railway.app/ws/chat/pricing/"
const ws = new WebSocket(endpoint + "?token=" + token)

ws.addEventListener('message', (event) => {
    console.log('Message from server ', event.data);
});

ws.addEventListener('close', (event) => {
    console.log('The connection has been closed successfully.');
});



