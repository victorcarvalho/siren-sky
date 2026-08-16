import './Homepage.css'
import { ImagesDisplay } from '../../components/ImagesDisplay/ImagesDisplay'
import { Header } from '../../components/Header/Header'
import { Buttons } from '../../components/Buttons/Buttons'
import { Advice } from '../../components/Advice/Advice'

export function Homepage({ imageInfo, setImageInfo }) {
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