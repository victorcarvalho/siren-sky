import React from 'react'
import './App.css'
import { ImagesDisplay } from './pages/ImagesDisplay';

function App() {
  const [imageInfo, setImageInfo] = React.useState([]);
  const inputRef = React.useRef();

  // function fakeApi() {
  //   return new Promise((resolve) => {
  //     setTimeout(() => {
  //       resolve(Math.random() < 0.5 ? 0 : 1);
  //     }, 1000); // espera 1 segundo
  //   });
  // }

  function handleImages(e) {
    const files = Array.from(e.target.files);
    if (!files) return;

    files.forEach((file) => {
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
        URL.revokeObjectURL(img.src);
      };
      img.src = URL.createObjectURL(file);
    })
  }

  // async function sendImage() {
  //   if (imageInfo.length === 0) {
  //     alert("Selecione uma imagem primeiro!");
  //     return;
  //   }

  //   console.log("Enviando...");

  //   const resultado = await fakeApi();

  //   if (resultado === 1) {
  //     alert("É lixo!");
  //   } else {
  //     alert("Não é lixo!");
  //   }
  // }

  return (
    <>
      <div className="sendImage">
        <button onClick={() => inputRef.current.click()}>Escolher imagem</button>
        <input
          multiple
          ref={inputRef}
          type="file"
          accept="image/*"
          onChange={handleImages}
          hidden
        />
        {/* <button type="button" onClick={sendImage}>Enviar</button> */}
      </div>
      {imageInfo.length > 0 && (
        <div>
          <ImagesDisplay imageInfo={imageInfo} />
        </div>
      )}
    </>
  )
}

export default App
