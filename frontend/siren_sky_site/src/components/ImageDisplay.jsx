import React from 'react'
import { createPortal } from "react-dom"
import './imageDisplay.css'

export function ImageDisplay({ imageInfo, setImageInfo, index }) {
	const [showImage, setShowImage] = React.useState(false);
	function removeImage() {
		setImageInfo(imageInfo.filter((_, i) => i !== index))
	}
	return (
		<>
			<tr>
				<td>{imageInfo[index].name}</td>
				<td>{(imageInfo[index].size / 1024).toFixed(2)} KB</td>
				<td>{imageInfo[index].width} px</td>
				<td>{imageInfo[index].height} px</td>
				<td>{imageInfo[index].state}</td>
				<td><button onClick={() => setShowImage(true)}>Visualizar</button></td>
				<td className="close" onClick={removeImage}><button><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 -960 960 960" width="24px" fill="#e3e3e3"><path d="m256-200-56-56 224-224-224-224 56-56 224 224 224-224 56 56-224 224 224 224-56 56-224-224-224 224Z" /></svg></button></td>
			</tr >
			{showImage &&
				createPortal(
					<div className='pop-up'>
						<div>
							<img src={URL.createObjectURL(imageInfo[index].img)} alt="Imagem" />
						</div>
						<button onClick={() => setShowImage(false)}>Fechar</button>
					</div>,
					document.body
				)
			}
		</>
	);
};