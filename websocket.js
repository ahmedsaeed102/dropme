let token ='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjgxMzk2MzUxLCJpYXQiOjE2Nzg4MDQzNTEsImp0aSI6ImZiNTc4NzVkYzlmNzQ1Y2E4MjBkMmQ3ODAzYWRiODBhIiwidXNlcl9pZCI6MTR9.9niez_A8isrxCgX7xibZPyT2xFrNSpI90Xp_lj2tfFI'
// let endpoint = "ws://localhost:8000/machines/recycle/start/machine/"
let endpoint = "wss://dropme.up.railway.app/machines/recycle/start/machine/"
const ws = new WebSocket(endpoint + "?token=" + token)

ws.addEventListener('message', (event) => {
    console.log('Message from server ', event.data);
});

ws.addEventListener('close', (event) => {
    console.log('The connection has been closed successfully.');
});
