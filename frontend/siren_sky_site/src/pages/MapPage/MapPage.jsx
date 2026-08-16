import { MapContainer, TileLayer, Marker, Popup } from "react-leaflet";
import "leaflet/dist/leaflet.css";

export function MapPage({ imageInfo }) {
	const locations = imageInfo.filter(
		image =>
			image.latitude !== "-" &&
			image.longitude !== "-" &&
			image.state === "Tem lixo"
	);

	return (
		<MapContainer
			center={[-5.79448, -35.211]}
			zoom={13}
			style={{
				width: "100%",
				height: "100vh"
			}}
		>
			<TileLayer
				attribution="&copy; OpenStreetMap contributors"
				url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
			/>

			{locations.map(image => (
				<Marker
					key={image.id}
					position={[
						image.latitude,
						image.longitude
					]}
				>
					<Popup>
						<strong>{image.name}</strong>
						<br />
						Latitude: {image.latitude}
						<br />
						Longitude: {image.longitude}
					</Popup>
				</Marker>
			))}
		</MapContainer>
	);
}