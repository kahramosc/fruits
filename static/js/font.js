function fonte(e) {

	var elemento = $(".fontControl");
	var fonte = parseInt(elemento.css('font-size'));

	var body = $("body");
	const fonteNormal = parseInt(body.css('font-size'));


	if (e == 'a') {
		fonte++;
	}
	if (e == 'd'){
		fonte--;
	}
	if (e == 'n'){
		fonte = fonteNormal;
	}

	elemento.css("fontSize", fonte);

}


function pagina(e) {

	var fonte = parseInt( document.body.style.zoom.replace("%",""));


	if(isNaN(fonte)){
	fonte = 100;
	}

	var body = $("body");

	if (e == 'a') {
		fonte = fonte + 10;
	}
	if (e == 'd'){
			fonte = fonte - 10;
	}
	if (e == 'n'){
		fonte = 100;
	}

	 document.body.style.zoom = fonte+"%";

}