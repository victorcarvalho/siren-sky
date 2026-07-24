import React from 'react'
import './imageDisplay.css'
export function ImageDisplay({ name, size, width, height, file }) {
	const [showImage, setShowImage] = React.useState(false);
	return (
		<tr>
			<td>{name}</td>
			<td>{(size / 1024).toFixed(2)} KB</td>
			<td>{width} px</td>
			<td>{height} px</td>
			<td>-</td>
			<td><button onClick={() => setShowImage(true)}>Visualizar</button></td>
			{showImage &&
				<div className='pop-up'>
					<div>
						<img src={URL.createObjectURL(file)} alt="Imagem" />
					</div>
					<button onClick={() => setShowImage(false)}>Fechar</button>
				</div>
			}
		</tr >
	);
};