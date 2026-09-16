import "./Info.css"

export function Info() {
	return (
		<>
			<div className="info-component">
				<div className="info-card">
					<p className="info-card-title">Imagens</p>
					<span className="info-card-number">0</span>
				</div>
				<div className="info-card">
					<p className="info-card-title">Processadas</p>
					<span className="info-card-number">0</span>
				</div>
				<div className="info-card">
					<p className="info-card-title">Dados de GPS ausentes</p>
					<span className="info-card-number">0</span>
				</div>
				<div className="info-card">
					<p className="info-card-title">Alertas de lixo</p>
					<span className="info-card-number">0</span>
				</div>
			</div>
		</>
	);
}