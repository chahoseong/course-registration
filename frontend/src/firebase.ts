import { initializeApp } from "firebase/app";
import { getAuth, connectAuthEmulator } from "firebase/auth";
import { getFirestore, connectFirestoreEmulator } from "firebase/firestore";

const firebaseConfig = {
  apiKey: import.meta.env.VITE_FIREBASE_API_KEY,
  authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN,
  projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID,
  storageBucket: import.meta.env.VITE_FIREBASE_STORAGE_BUCKET,
  messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID,
  appId: import.meta.env.VITE_FIREBASE_APP_ID
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);

// Initialize Services
export const auth = getAuth(app);

// Use default DB unless a named DB is explicitly configured.
const firestoreDatabaseId = import.meta.env.VITE_FIREBASE_DATABASE_ID?.trim();
const useDefaultDatabase = !firestoreDatabaseId || firestoreDatabaseId === "(default)";

console.log(
  `[Firebase] Firestore DB: ${useDefaultDatabase ? "(default)" : firestoreDatabaseId}`
);

export const db = useDefaultDatabase
  ? getFirestore(app)
  : getFirestore(app, firestoreDatabaseId);

// Connect to Emulators in local environment
if (window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1") {
  connectAuthEmulator(auth, "http://127.0.0.1:9099");
  connectFirestoreEmulator(db, "127.0.0.1", 8080);
  console.log("Connected to Firebase Emulators");
}

export default app;
