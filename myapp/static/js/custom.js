function myType(){
  $("#item_type").val($(".de_nav li.active span").text());
}


function mySeason(){
  $("#season").val($("#item_input_season").text());
}


// live changes preview items 
$(document).ready(()=>{
  $('#upload_file').change(function(){
    const file = this.files[0];
        // console.log(file);
        if (file){
          let reader = new FileReader();
          reader.onload = function(event){
            // console.log(event.target.result);
            $('#preview_image').attr('src', event.target.result);
        }
        reader.readAsDataURL(file);
    }
});
});


function myDateContract(){

  // var date = new Date($('#expiration_date_contract').val());
  // var hours = date.getHours();
  // var day = date.getDate() +1;
  // var month = date.getMonth() + 1;
  // var year = date.getFullYear();
  // alert([month, day, year].join('/'));



  // $('#p').data("hour",hours);
  // $('#p').data("month",month);
  // $('#p').data("day",day);
  // $('#p').data("year",year);


// $('#p').append($('<div class="de_countdown" data-year="2024" data-month="2" data-day="16" data-hour="8" ></div>');


}

function myDateService(){

  // var date = new Date($('#expiration_date_service').val());
  // var hours = date.getHours();
  // var day = date.getDate() +1;
  // var month = date.getMonth() + 1;
  // var year = date.getFullYear();
  // alert([month, day, year].join('/'));

  // $('#p').data("hour",hours);
  // $('#p').data("month",month);
  // $('#p').data("day",day);
  // $('#p').data("year",year);

}

function myTitle(){

    $("#preview_title").text($("#item_title").val());

}


function myPrice(){


    $("#preview_price").text($('#item_price').val() + ' USD');


}

function myAuction(){

    if($('#switch-unlock').prop("checked") == true){

      $('#preview_auction').show();
  }else{

      $('#preview_auction').hide();

  }
}

function myLoad(){

    const date = new Date();

    const day = date.getDate();
    const month = date.getMonth() + 1;
    const year = date.getFullYear();

    $('#preview_auction').hide();

    $('#preview_duration_timestamp').text(month + '/' + day + '/' + year);





}

