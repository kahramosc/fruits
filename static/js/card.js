
$( ".btnMenosCard" ).click(function() {

  var oferta = String(this.id).split("_")[1]
  var carrinho = String(this.id).split("_")[2]

  var quantity = parseInt($("#quantityText_"+oferta+"_"+carrinho).val());

  if(quantity > 1){
    quantity = quantity - 1;
  }

 updateCardItem(oferta,carrinho,quantity)

});

$( ".btnMaisCard" ).click(function() {
   var oferta = String(this.id).split("_")[1]
  var carrinho = String(this.id).split("_")[2]

  var quantity = parseInt($("#quantityText_"+oferta+"_"+carrinho).val());

    quantity = quantity + 1;

 updateCardItem(oferta,carrinho,quantity)
});

function updateCardItem(oferta,carrinho,quantidade) {

    $.ajax({
      type: "POST",
      contentType: "application/json; charset=utf-8",
      url: "/linkUpdateCardItens",
      data: JSON.stringify({oferta: oferta, carrinho: carrinho,
      quantidade: quantidade}),
      success: function (data) {

        window.location.replace("/card");

      },
      dataType: "json"
    });

}