export function ImageDisplay({name, size, width, height}) {
	return (
		<div>
			<p>Nome: {name}</p>
			<p>Tamanho: {(size / 1024).toFixed(2)} KB</p>
			<p>Largura: {width} px</p>
			<p>Altura: {height} px</p>
		</div>
	);
};