( function(app, $) {
	
	//app.name('Computer a Example');
	/*
	app.win_html( { 'main':  });
	app.reg_event(
      'click', //first param is the evt
      'button', //second param is the selector
       function( elem ){
       	  app.log('window:' + app.win_id(), 'clicked!' );
       }
	);*/
	
	console.log('rewrite app.win_html');
	app.win_html = function(){
		return {
			win_content: app.app_data().tpl.win_content,
			win_bottom: app.app_data().tpl.win_bottom
		};
	};
	
	console.log('computer.js', app);

})(app, jQuery);