import { ImageDisplay } from './ImageDisplay'
import './ImagesDisplay.css'

export function ImagesDisplay({ imageInfo, setImageInfo }) {
	return (
		<div className='imagesdisplay'>
			<table>
				<colgroup>
					<col style={{ width: "30%" }} />
					<col style={{ width: "15%" }} />
					<col style={{ width: "10%" }} />
					<col style={{ width: "10%" }} />
					<col style={{ width: "15%" }} />
					<col style={{ width: "15%" }} />
					<col style={{ width: "5%" }} />
				</colgroup>
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
		</div>
	)
}