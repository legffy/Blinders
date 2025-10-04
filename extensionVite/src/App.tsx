function App() {
  return (
    <div className="min-h-screen max-w-screen flex flex-col items-center justify-center bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500 text-white">
      <div className="bg-black/50 rounded-2xl shadow-xl p-8 max-w-sm text-center">
        <h1 className="text-3xl font-extrabold mb-4">Blinders</h1>
        <p className="mb-6 text-sm opacity-80">
          If you can see a gradient background, rounded box, and white text,
          Tailwind is working 🎉
        </p>
        <button className="px-4 py-2 rounded-lg bg-green-400 text-black font-bold hover:bg-green-500 transition">
          Test Button
        </button>
      </div>
    </div>
  );
}

export default App;