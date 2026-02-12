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

const rawDatabaseId = import.meta.env.VITE_FIREBASE_DATABASE_ID || "course-registration";
const firestoreDatabaseId = rawDatabaseId.trim();

if (!import.meta.env.VITE_FIREBASE_DATABASE_ID) {
  console.warn("[firebase] VITE_FIREBASE_DATABASE_ID is missing. Falling back to default:", firestoreDatabaseId);
} else {
  console.info("[firebase] VITE_FIREBASE_DATABASE_ID loaded from env:", firestoreDatabaseId);
}

export const db = getFirestore(app, firestoreDatabaseId);

// Connect to Emulators in local environment
if (window.location.hostname === "localhost") {
  connectAuthEmulator(auth, "http://localhost:9099");
  connectFirestoreEmulator(db, "localhost", 8080);
  console.log("Connected to Firebase Emulators");
}

export default app;
