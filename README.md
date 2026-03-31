# jarvis
🧠 J.A.R.V.I.S. Multimodal Neural InterfaceA browser-based, highly interactive multimodal AI assistant inspired by Iron Man's J.A.R.V.I.S.Powered by React, Tailwind CSS, and the latest Google Gemini 2.5 Flash models, this application supports real-time text processing, voice synthesis (TTS/STT), visual intelligence (Image-to-Text), and live web-grounded search capabilities—all packed into a sleek, futuristic terminal UI.✨ Key Features🌐 Live Web Search: Toggle real-time grounding to allow J.A.R.V.I.S. to fetch up-to-the-minute data from Google Search. Clickable source links are provided in the UI.👁️ Vision Pro (Multimodal): Drag, drop, or upload images directly into the terminal. Ask J.A.R.V.I.S. to analyze the contents, extract text, or describe the scene.🎙️ Advanced Voice Synthesis: Utilizes Gemini's high-fidelity Text-to-Speech (gemini-2.5-flash-preview-tts) for incredibly natural vocal responses. Speech-to-Text is also supported via native Web Speech APIs.🎯 Tactical Planning & Diagnostics: Built-in shortcut commands force the LLM to analyze conversation history or formulate step-by-step strategic plans.🔐 Secure Key Override: Easily plug in an alternative Gemini API key directly through the UI footer for testing without touching the code.🚀 Quick Start (Local Setup)To run this application on your local machine (Windows, Mac, or Linux), you will need Node.js installed.1. Initialize a Vite React Projectnpm create vite@latest jarvis-interface -- --template react
cd jarvis-interface
2. Install DependenciesInstall Tailwind CSS and Lucide React (for the futuristic icons):npm install lucide-react
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
Configure your tailwind.config.js:/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
Add Tailwind directives to your src/index.css:@tailwind base;
@tailwind components;
@tailwind utilities;
3. Add the CodeReplace the contents of src/App.jsx with the App.jsx file from this repository.4. Setup Environment VariablesCreate a .env file in the root of your project and add your Google Gemini API Key. (You can get a free key from Google AI Studio):VITE_GEMINI_API_KEY="AIzaSyYourApiKeyHere..."
5. Run the Systemnpm run dev
Open http://localhost:5173 in your browser. All systems are go!🛠️ Architecture NotesFail-Fast Error Handling: The app implements smart exponential backoff but immediately halts and displays UI errors for 401/403 authentication issues or 404 model access errors.PCM to WAV Conversion: The application features a custom in-memory binary parser to convert Gemini's raw audio/L16 PCM output into playable .wav blobs on the fly.Cross-Platform: As a standard React/Web app, J.A.R.V.I.S. runs perfectly on Desktop and Mobile browsers without native OS dependencies.🤝 ContributingPull requests are welcome! If you want to add new LLM tools (like calendar integration or local file system access via File System Access API), feel free to fork the repository.“Just as I always say: Keep your friends rich and your enemies rich, and wait to find out which is which.” — Tony Stark
