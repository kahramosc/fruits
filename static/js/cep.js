


$( "#btnBuscarCep" ).click(function() {
  BuscarCep();
});

$( "#StCep" ).focus(function() {
  BuscarCep();
});

$('#StCep').keypress(
function(e) {
    if (e.keyCode == 5) {
        e.preventDefault();
        BuscarCep();
    }
});


function BuscarCep() {

	if ($('#StCep').val() == null || $('#StCep').val() == "") {

		return;

	}

	cep = $('#StCep').val();

        urlcep = 'https://viacep.com.br/ws/'+ cep +'/json/';

	$.ajax({
		type : "post",
		url : urlcep,		
		dataType : "jsonp",
		async : true,
		cache : false,
		success : function(ret) {

			try {


				// $('#StLagradouro').text(ret.dados.valorDesconto));
				$('#StLagradouro').val(ret.logradouro);
				$('#StNumero').val("");
				$('#StBairro').val(ret.bairro);
				$('#StCidade').val(ret.localidade);
				$('#StEstado').val(ret.uf);


				$(".addres").css({visibility:"visible", opacity: 0.0}).animate({opacity: 1.0},200);

			} catch (e) {
			   $(".addres").css({visibility:"visible", opacity: 0.0}).animate({opacity: 1.0},200);
				console.log(e);
			}


		},
		error : function(x, e) {
			$("#StCep").val("");
			$('#StLagradouro').text("");
			$('#StNumero').text("");
			$('#StBairro').text("");
			$('#StCidade').text("");
			$('#StEstado').text("");


			$(".addres").css({visibility:"visible", opacity: 0.0}).animate({opacity: 1.0},200);


			setError(x, e);

		}
	});

}