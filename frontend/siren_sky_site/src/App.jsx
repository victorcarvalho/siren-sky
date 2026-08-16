import { Routes, Route } from "react-router"
import { Homepage } from "./pages/Homepage/Homepage"
import { useState } from "react";
import { MapPage } from "./pages/MapPage/MapPage"
import './App.css'


function App() {
  const [imageInfo, setImageInfo] = useState([]);
  return (
    <Routes>
      <Route path="/" element={<Homepage imageInfo={imageInfo} setImageInfo={setImageInfo} />} />
      <Route path="/sirensky" element={<Homepage />} />
      <Route path="/map" element={<MapPage imageInfo={imageInfo} />} />
    </Routes>
  )
}

export default App
