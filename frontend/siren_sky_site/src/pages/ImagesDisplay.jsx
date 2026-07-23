import { ImageDisplay } from './ImageDisplay'

export function ImagesDisplay({ imageInfo }) {
	return (
		<>
			{
				imageInfo.map((i) => {
					return (
						<ImageDisplay
							name={i.name}
							size={i.size}
							width={i.width}
							height={i.height}
							key={i.id}
						/>
					);
				})
			}
		</>
	)
}