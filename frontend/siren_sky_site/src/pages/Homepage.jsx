import React from 'react'
import './Homepage.css'
import { ImagesDisplay } from '../components/ImagesDisplay';
import { Header } from '../components/Header';

export function Homepage() {
	const [imageInfo, setImageInfo] = React.useState([]);
	const inputRef = React.useRef();

	function handleImages(e) {
		const files = Array.from(e.target.files);
		if (!files) return;

		files.forEach((file) => {
			const img = new Image();
			img.onload = () => {
				setImageInfo((prev) => [
					...prev,
					{
						id: crypto.randomUUID(),
						img: file,
						name: file.name,
						size: file.size,
						width: img.width,
						height: img.height,
						state: "-"
					}]);
				URL.revokeObjectURL(img.src);
			};
			img.src = URL.createObjectURL(file);
		})
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
		<>
			<Header />
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
				{imageInfo.length > 0 &&
					<button onClick={() => {
						imageInfo.forEach((i, index) => {
							if (i.state === "-") {
								sendImage(i.img, index)
							}
						})
					}}>Classificar imagens</button>
				}
			</div>
			{imageInfo.length > 0 && (
				<div>
					<ImagesDisplay imageInfo={imageInfo} setImageInfo={setImageInfo} />
				</div>
			)}
		</>
	)
}