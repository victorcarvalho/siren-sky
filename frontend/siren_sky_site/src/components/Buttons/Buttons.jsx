import React from 'react'
import './Buttons.css'
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

	function handleDrop(event) {
		event.preventDefault();

		const files = event.dataTransfer.files;

		handleImages({ target: { files } });
	}

	return (
		<div className='buttons-component'>
			<h1 className="buttons-title">Enviar imagens para classificação</h1>
			<div
				className="buttons-dropArea"
				onClick={() => inputRef.current.click()}
				onDragOver={(event) => event.preventDefault()}
				onDrop={handleDrop}
			>
				<svg className="buttons-dropArea-sendIcon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 640"><path d="M176 544C96.5 544 32 479.5 32 400C32 336.6 73 282.8 129.9 263.5C128.6 255.8 128 248 128 240C128 160.5 192.5 96 272 96C327.4 96 375.5 127.3 399.6 173.1C413.8 164.8 430.4 160 448 160C501 160 544 203 544 256C544 271.7 540.2 286.6 533.5 299.7C577.5 320 608 364.4 608 416C608 486.7 550.7 544 480 544L176 544zM337 255C327.6 245.6 312.4 245.6 303.1 255L231.1 327C221.7 336.4 221.7 351.6 231.1 360.9C240.5 370.2 255.7 370.3 265 360.9L296 329.9L296 432C296 445.3 306.7 456 320 456C333.3 456 344 445.3 344 432L344 329.9L375 360.9C384.4 370.3 399.6 370.3 408.9 360.9C418.2 351.5 418.3 336.3 408.9 327L336.9 255z" /></svg>
				<p className="buttons-dropArea-description">
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
					<button className="buttons-classify" onClick={() => {
						imageInfo.forEach((i, index) => {
							if (i.state === "-") {
								sendImage(i.img, index)
							}
						})
					}}>Classificar imagens</button>
				</>
			}
		</div>
	)
}