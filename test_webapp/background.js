var firebaseConfig = {
  apiKey: "AIzaSyDhwAFrV59IrLW4RvVzIPlNlZHEQHRpfhU",
  authDomain: "hackthenorth2019-f2fcd.firebaseapp.com",
  databaseURL: "https://hackthenorth2019-f2fcd.firebaseio.com",
  projectId: "hackthenorth2019-f2fcd",
  storageBucket: "",
  messagingSenderId: "65543075988",
  appId: "1:65543075988:web:d3a4b3723e27d4a39f1c81"
};

firebase.initializeApp(firebaseConfig);

const appDb = firebase.database().ref();
const applicationState = { values: [] };

chrome.tabs.onUpdated.addListener((tabId, change, tab) => {
  if (change.url) {
    console.log(change.url);
    appDb.child("ActiveURL").set(change.url);
    console.log("succesfully wrote to firebase")
  }
});