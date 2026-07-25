import { ImageDisplay } from './ImageDisplay'
import './ImagesDisplay.css'

export function ImagesDisplay({ imageInfo, setImageInfo }) {
	return (
		<table>
			<thead>
				<tr>
					<th>Nome</th>
					<th>Tamanho</th>
					<th>Largura</th>
					<th>Altura</th>
					<th>Situação</th>
					<th>Imagem</th>
				</tr>
			</thead>
			<tbody>
				{
					imageInfo.map((i, index) => {
						return (
							<ImageDisplay
								imageInfo={imageInfo}
								setImageInfo={setImageInfo}
								index={index}
								key={i.id}
							/>
						);
					})
				}
			</tbody>
		</table>
	)
}