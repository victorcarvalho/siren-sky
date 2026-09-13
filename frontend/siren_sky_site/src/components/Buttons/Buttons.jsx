import React from 'react'
import './Buttons.css'
import { Link } from 'react-router'
import exifr from 'exifr'

export function Buttons({ imageInfo, setImageInfo }) {
	const inputRef = React.useRef();

	async function handleImages(e) {
		const files = Array.from(e.target.files);
		if (!files.length) return;

		files.forEach((file) => {
			const img = new Image();

			img.onload = async () => {
				const gps = await exifr.gps(file);

				const latitude = gps && Number.isFinite(gps.latitude)
					? gps.latitude
					: "-";

				const longitude = gps && Number.isFinite(gps.longitude)
					? gps.longitude
					: "-";

				setImageInfo((prev) => [
					...prev,
					{
						id: crypto.randomUUID(),
						img: file,
						name: file.name,
						size: file.size,
						width: img.width,
						height: img.height,
						latitude: latitude,
						longitude: longitude,
						state: "-"
					}
				]);

				URL.revokeObjectURL(img.src);
			};

			img.src = URL.createObjectURL(file);
		});
	}

	async function sendImage(image, index) {
		console.log("Requisação realizada...")
		const formData = new FormData();

		formData.append("teste", image); // O primeiro argumento é o campo enviado para a API

		const response = await fetch("http://127.0.0.1:5000/verificar_lixo", {
			method: "POST",
			body: formData
		});

		const data = await response.text();

		setImageInfo((prev) => {
			return prev.map((item, j) =>
				j === index
					? {
						...item,
						state: data === "1" ? "Tem lixo" : "Sem lixo"
					} :
					item
			)
		})
	}
	return (
		<div className='buttons-component'>
			<h1 className="buttons-title">Enviar imagens para classificação</h1>
			<div
				className="buttons-dropArea"
				onClick={() => inputRef.current.click()}
				onDragOver={(event) => event.preventDefault()}
			// onDrop={handleDrop}
			>

				<p>
					Arraste e solte suas imagens aqui<br />
					ou clique para selecionar
				</p>

				<button type="button">
					Selecionar arquivos
				</button>

				<input
					multiple
					ref={inputRef}
					type="file"
					accept="image/*"
					onChange={handleImages}
					hidden
				/>
			</div>
			{imageInfo.length > 0 &&
				<>
					<button onClick={() => {
						imageInfo.forEach((i, index) => {
							if (i.state === "-") {
								sendImage(i.img, index)
							}
						})
					}}>Classificar imagens</button>
					<Link to="/map"><button>Mapa</button></Link>
				</>
			}
		</div>
	)
}