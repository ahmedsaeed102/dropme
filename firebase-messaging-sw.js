importScripts('https://www.gstatic.com/firebasejs/9.1.0/firebase-app-compat.js');
importScripts('https://www.gstatic.com/firebasejs/9.1.0/firebase-messaging-compat.js');


const firebaseConfig = {
    apiKey: "AIzaSyCL_0pSXvljIsASqeHH-4ta2rIsmdCdYLw",
    authDomain: "dropmenotifiy.firebaseapp.com",
    projectId: "dropmenotifiy",
    storageBucket: "dropmenotifiy.appspot.com",
    messagingSenderId: "716164501655",
    appId: "1:716164501655:web:be990d2e6def4f71f499d2"
};
const app = firebase.initializeApp(firebaseConfig);

const messaging = app.messaging();

