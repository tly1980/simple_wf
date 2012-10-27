var AJLoader;
(function(){
   function create_loader(file_input_id, url){
      var xhr = new XMLHttpRequest(); 

      return {
        upload: function (){
           var fileInput = document.getElementById(file_input_id);
           var file = fileInput.files[0];
           var formData = new FormData();
           formData.append('file', file);
           formData.append('f_name', file.fileName);
           xhr.open('POST', url, true);
           xhr.send(formData);
        },

        on: function(e, e_hander){
            if (xhr.upload !== undefined ){
                xhr.upload.addEventListener(e, e_hander);
            }else{
                if (console !== undefined ){
                  console.log('xhr.event is unsupported!');
                }
            }
        }
     };

  }

  AJLoader = create_loader;
  return AJLoader; 
})();

//upload event:
//loadstart
//progress
//load
//readystatechange