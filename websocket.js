let token ='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjgyNTEzNjEwLCJpYXQiOjE2Nzk5MjE2MTAsImp0aSI6IjhlYTU0MGRhMDQwYjQ2N2Q5NTczNGNjM2U1ODhhZjY2IiwidXNlcl9pZCI6Mn0.XMfLpsREKvXMRfXI9jndBtcdG2Z0qfA-fw5sH3FS9l4'
// let endpoint = "ws://localhost:8000/machines/recycle/start/machine/"
let endpoint = "wss://dropme.up.railway.app/machines/recycle/start/machine/"
const ws = new WebSocket(endpoint + "?token=" + token)

ws.addEventListener('message', (event) => {
    console.log('Message from server ', event.data);
});

ws.addEventListener('close', (event) => {
    console.log('The connection has been closed successfully.');
});
