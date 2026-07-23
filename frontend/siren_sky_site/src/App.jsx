import React from 'react'
import './App.css'
import { ImagesDisplay } from './pages/ImagesDisplay';

function App() {
  // const [image, setImage] = React.useState(null);
  const [imageInfo, setImageInfo] = React.useState([]);
  // const [imagePreview, setImagePreview] = React.useState(false);

  // async function sendImage() {
  //   if (imageInfo != [{}]) {
  //     alert("Selecione uma imagem primeiro!")
  //     return
  //   }
  //   console.log("Requisação realizada...")
  //   const formData = new FormData();

  //   formData.append("teste", imageInfo.img); // O primeiro argumento é o campo enviado para a API

  //   const response = await fetch("https://sirensky.nocs.ifrn.br/verificar_lixo", {
  //     method: "POST",
  //     body: formData
  //   });

  //   const data = await response.json(); // Só funciona se a API retornar um json

  //   console.log(data);
  // }

  return (
    <>
      <div className="sendImage">
        <input
          type="file"
          accept="image/*"
          onChange={(e) => {
            const file = e.target.files[0];
            if (!file) return;

            const img = new Image();
            img.onload = () => {
              setImageInfo((prev) => [
                ...prev,
                {
                  img: file,
                  name: file.name,
                  size: file.size,
                  width: img.width,
                  height: img.height,
                  id: crypto.randomUUID()
                }]);
            };

            img.src = URL.createObjectURL(file)
          }}
        />
        {/* <button type="button" onClick={sendImage}>Enviar</button> */}
      </div>
      {imageInfo.length && (
        <div>
          <ImagesDisplay imageInfo={imageInfo} />
        </div>
      )}
    </>
  )
}

export default App
