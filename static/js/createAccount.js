$( "#createAccount" ).click(function() {
  insertUser();
});

function insertUser() {

     var dict = {
        nome: $('#StNome').val(),
      email: $('#StEmail').val(),
      senha: $('#StSenha').val(),
      cep: $('#StCep').val(),
      lagradouro: $('#StLagradouro').val(),
      numero: $('#StNumero').val(),
      cidade: $('#StCidade').val(),
      estado: $('#StEstado').val(),
      bairro: $('#StBairro').val(),
      complemento: $('#StComplemento').val()
      };

    $.ajax({
      type: "POST",
      async: true,
      contentType: "application/json; charset=utf-8",
      url: "/insertUser",
      data: JSON.stringify(dict),
      success: function (data) {

        window.location.replace("/home");

      },
      dataType: "json"
    });

}