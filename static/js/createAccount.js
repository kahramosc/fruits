$( "#createAccount" ).click(function() {
  insertUser();
});

function insertUser() {

    $.ajax({
      type: "POST",
      contentType: "application/json; charset=utf-8",
      url: "/insertUser",
      data: JSON.stringify({nome: $('#StNome').val(), email: $('#StEmail').val()}),
      success: function (data) {
        console.log(data.nome);
        console.log(data.email);
        window.location.replace("/home");

      },
      dataType: "json"
    });

}