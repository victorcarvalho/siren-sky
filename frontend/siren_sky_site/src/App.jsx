import { Routes, Route } from "react-router"
import { Homepage } from "./pages/Homepage/Homepage"
import './App.css'


function App() {
  return (
    <Routes>
      <Route path="/" element={<Homepage />} />
      <Route path="/sirensky" element={<Homepage />} />
    </Routes>
  )
}

export default App
