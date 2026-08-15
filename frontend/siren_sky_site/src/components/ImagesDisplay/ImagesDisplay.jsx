import { ImageDisplay } from '../ImageDisplay/ImageDisplay'
import './ImagesDisplay.css'

export function ImagesDisplay({ imageInfo, setImageInfo }) {
	return (
		<div className='imagesdisplay'>
			<table>
				{/* <colgroup>
					<col style={{ width: "11%" }} />
					<col style={{ width: "12.5%" }} />
					<col style={{ width: "12.5%" }} />
					<col style={{ width: "12.5%" }} />
					<col style={{ width: "12.5%" }} />
					<col style={{ width: "12.5%" }} />
					<col style={{ width: "12.5%" }} />
					<col style={{ width: "12.5%" }} />
					<col style={{ width: "12.5%" }} />
				</colgroup> */}
				<thead>
					<tr>
						<th>Nome</th>
						<th>Latitude</th>
						<th>Longitude</th>
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