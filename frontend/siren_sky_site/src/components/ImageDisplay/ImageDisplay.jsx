import React from 'react'
import { createPortal } from "react-dom"
import './ImageDisplay.css'

export function ImageDisplay({ imageInfo, setImageInfo, index }) {
	const [showImage, setShowImage] = React.useState(false);
	function removeImage() {
		setImageInfo(imageInfo.filter((_, i) => i !== index))
	}
	return (
		<>
			<tr>
				<td>{imageInfo[index].name}</td>
				<td>{imageInfo[index].latitude}</td>
				<td>{imageInfo[index].longitude}</td>
				<td>{(imageInfo[index].size / 1024).toFixed(2)} KB</td>
				<td>{imageInfo[index].width} px</td>
				<td>{imageInfo[index].height} px</td>
				<td>{imageInfo[index].state}</td>
				<td><button onClick={() => setShowImage(true)}>Visualizar</button></td>
				<td><button onClick={removeImage} className='closeIcon'><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 -960 960 960"><path d="m256-200-56-56 224-224-224-224 56-56 224 224 224-224 56 56-224 224 224 224-56 56-224-224-224 224Z" /></svg></button></td>
			</tr >
			{showImage &&
				createPortal(
					<div className='pop-up'>
						<div>
							<img src={URL.createObjectURL(imageInfo[index].img)} alt="Imagem" />
							<button onClick={() => setShowImage(false)} className='closeIcon'><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 -960 960 960"><path d="m256-200-56-56 224-224-224-224 56-56 224 224 224-224 56 56-224 224 224 224-56 56-224-224-224 224Z" /></svg></button>
						</div>
						<button onClick={() => setShowImage(false)}>Fechar</button>
					</div>,
					document.body
				)
			}
		</>
	);
};