import React from 'react'
import './Homepage.css'
import { ImagesDisplay } from '../components/ImagesDisplay'
import { Header } from '../components/Header'
import { Buttons } from '../components/Buttons'
import { Advice } from '../components/Advice'

export function Homepage() {
	const [imageInfo, setImageInfo] = React.useState([]);
	return (
		<>
			<Header />
			<Buttons imageInfo={imageInfo} setImageInfo={setImageInfo} />
			{imageInfo.length > 0 ?
				<ImagesDisplay imageInfo={imageInfo} setImageInfo={setImageInfo} />
				:
				<Advice content="Envie as imagens para a verificação de lixo" />
			}
		</>
	)
}