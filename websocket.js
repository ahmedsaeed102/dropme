let token ='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjg0NzY1MTg5LCJpYXQiOjE2ODIxNzMxODksImp0aSI6Ijc5NTFmMzFkMGI4MTQ3MmQ4ZGJlYWFhODA2N2MwOWM0IiwidXNlcl9pZCI6Mn0.F0ofwwJEK_ZbPfFK9uYtqDs559EkeZjccvxHZufb2Fs'
// let endpoint = "ws://localhost:8000/machines/recycle/start/machine/"
let endpoint = "wss://dropme.onrender.com/machines/recycle/start/machine/"
const ws = new WebSocket(endpoint + "?token=" + token)

ws.addEventListener('message', (event) => {
    console.log('Message from server ', event.data);
});

ws.addEventListener('close', (event) => {
    console.log('The connection has been closed successfully.');
});
