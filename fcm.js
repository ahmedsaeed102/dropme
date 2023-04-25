import { initializeApp } from "https://www.gstatic.com/firebasejs/9.19.1/firebase-app.js";
import { getMessaging, getToken, onMessage } from "https://www.gstatic.com/firebasejs/9.19.1/firebase-messaging.js"

// Your web app's Firebase configuration

const firebaseConfig = {
    apiKey: "AIzaSyCL_0pSXvljIsASqeHH-4ta2rIsmdCdYLw",
    authDomain: "dropmenotifiy.firebaseapp.com",
    projectId: "dropmenotifiy",
    storageBucket: "dropmenotifiy.appspot.com",
    messagingSenderId: "716164501655",
    appId: "1:716164501655:web:be990d2e6def4f71f499d2"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const messaging = getMessaging(app);


requestPermission()

getToken(messaging, { vapidKey: 'BH-Tqv50WY9US7Bkdox-iONNS3TcksPgMVPNsZESc0SphayQcZMVzQAB66DlHP66eTCq3rl_4S0h6K72C5ePeug' }).then((currentToken) => {
    if (currentToken) {
        fetch('https://dropme.up.railway.app/user_register/devices/', {
            method: 'POST',
            headers: {
                'Accept': 'application/json, text/plain, */*',
                'Content-Type': 'application/json',
                'authorization':'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjg0OTQ1MTcyLCJpYXQiOjE2ODIzNTMxNzIsImp0aSI6ImRjNmM1YjQ2NGFkNTRhNDI5MzI4NDAxOWYzZTliNDI2IiwidXNlcl9pZCI6MX0.5w1BgaZLO24NBnaqTkLiIkFaRhm432vcTRBeZ1Vom9Y'
            },
            body: JSON.stringify({ "registration_id": currentToken, type: 'web' })
        }).then(res => res.json()).then(res => console.log(res));

    } else {
        // Show permission request UI
        console.log('No registration token available. Request permission to generate one.');
        // ...
    }
}).catch((err) => {
    console.log('An error occurred while retrieving token. ', err);
    // ...
});
function requestPermission() {
    console.log('Requesting permission...');
    Notification.requestPermission().then((permission) => {
        if (permission === 'granted') {
            console.log('Notification permission granted.');
        }
    })
}

onMessage(messaging, (payload) => {
    console.log('Message received. ', payload);
    // ...
});
