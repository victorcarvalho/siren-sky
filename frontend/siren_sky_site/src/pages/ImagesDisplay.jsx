import { ImageDisplay } from './ImageDisplay'
import './ImagesDisplay.css'

export function ImagesDisplay({ imageInfo }) {
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
			{
				imageInfo.map((i) => {
					return (
						<ImageDisplay
							name={i.name}
							size={i.size}
							width={i.width}
							height={i.height}
							file={i.img}
							key={i.id}
						/>
					);
				})
			}
		</table>
	)
}