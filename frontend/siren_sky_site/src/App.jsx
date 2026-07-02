import React from 'react'
import './App.css'

function App() {
  const [image, setImage] = React.useState(null);

  async function sendImage() {
    if (!image) {
      alert("Selecione uma imagem primeiro!")
      return
    }
    console.log("Requisação realizada...")
    const formData = new FormData();

    formData.append("teste", image); // O primeiro argumento é o campo enviado para a API

    const response = await fetch("https://sirensky.nocs.ifrn.br/verificar_lixo", {
      method: "POST",
      body: formData
    });

    const data = await response.json(); // Só funciona se a API retornar um json

    console.log(data);
  }

  return (
    <div className="sendImage">
      <input
        type="file"
        accept="image/*"
        onChange={(e) => setImage(e.target.files[0])}
      />
      <button type="button" onClick={sendImage}>Enviar</button>
    </div>
  )
}

export default App
