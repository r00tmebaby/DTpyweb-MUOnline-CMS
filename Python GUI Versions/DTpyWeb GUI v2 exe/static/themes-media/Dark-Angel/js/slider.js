$(document).ready(function() { 
						   
	var slides = $(".slider .slides").children(".slide"); 
	var width = $(".slider .slides").width(); 
	var i = slides.length; 
	var offset = i * width; 
	var cheki = i-1;
	
	$(".slider .slides").css('width',offset); 
	
	for (j=0; j < slides.length; j++) {
		if (j==0) {
			$(".slider .navigation").append("<div class='dot active'></div>");
		}
		else {
			$(".slider .navigation").append("<div class='dot'></div>");
		}
	}
	
	var dots = $(".slider .navigation").children(".dot");
	offset = 0;
	i = 0; 
	
	$('.slider .navigation .dot').click(function(){
		$(".slider .navigation .active").removeClass("active");								  
		$(this).addClass("active");
		i = $(this).index();
		offset = i * width;

		$('.slide').removeClass('active');
		var index=offset/width+1;
		$('.slider .slide:nth-child('+(index)+')').addClass('active');
		
		$(".slider .slides").css("transform","translate3d(-"+offset+"px, 0px, 0px)"); 
	});
	
	
	
	$("body .slider .next").click(function(){	
		if (offset < width * cheki) {	
			offset += width; 

			$('.slide').removeClass('active');
			var index=offset/width+1;
			$('.slider .slide:nth-child('+(index)+')').addClass('active');
		
			$(".slider .slides").css("transform","translate3d(-"+offset+"px, 0px, 0px)"); 
			$(".slider .navigation .active").removeClass("active");	
			$(dots[++i]).addClass("active");
		}
	});


	$("body .slider .prev").click(function(){	
		if (offset > 0) { 
			offset -= width;

			$('.slide').removeClass('active');
			var index=offset/width+1;
			$('.slider .slide:nth-child('+(index)+')').addClass('active');
		
			$(".slider .slides").css("transform","translate3d(-"+offset+"px, 0px, 0px)"); 
			$(".slider .navigation .active").removeClass("active");	
			$(dots[--i]).addClass("active");
		}
	});
	function autoSlide(){
		 if ($(".slider .navigation .active").index() < $(".slider .slides").children(".slide").length-1) {
		  $("body .slider .next").click();
		 } else {
		  $('.slider .navigation .dot:first-child').click();
		 }
		}
	setInterval(function(){ autoSlide(); }, 7000);
});