var apigClient = apigClientFactory.newClient();


function search_photos() {
  console.log("search_photos");
  var search_term = document.getElementById("searchbar").value;
  console.log(search_term);

  var params = {
    'q': search_term
  };

  var additionalParams = {
    headers: {
      'accept': 'application/json'
    }
  }

  apigClient.searchGet(params, {}, additionalParams).then(
    function (result) {
      image_urls = result["data"]["body"] || '';

      image_inner_html = $('#images');
      image_inner_html.html('');

      for (var i = 0; i < image_urls.length; i++) {
        image_inner_html.append('<img src="' + image_urls[i] + '" class="img-thumbnail">');
      }

    }
  ).catch(function (result) {
    console.log(result);
  });


  for (var i = 0; i < image_urls.length; i++) {
    image_inner_html.append('<img src="' + image_urls[i] + '" class="img-thumbnail">');
  }
}

function toggleUploadHandler() {
    var handler = document.querySelector('.upload_photo_handler');
    if (handler.style.display === 'none' || handler.style.display === '') {
        handler.style.display = 'block'; // Show the handler
    } else {
        handler.style.display = 'none'; // Hide the handler
    }
}


function upload_photos() {
  console.log("upload_photos");

  var file_path = $('#file').val().split('\\');
  var file_name = file_path[file_path.length - 1];

  var file = $('#file')[0].files[0];

  var additional_labels = $('#labels').val() || '';
  console.log(additional_labels);

  var additionalParams = {
    headers: {
      'Content-Type': file.type,
      'accept': 'application/json',
    }
  }
  const timestamp = new Date().getTime();

  var folderName = 'imagebuck'
  var imageName = file_name + '-' + timestamp.toString(36)

  var params = {
    object: imageName,
    folder: folderName,
    'x-amz-meta-customLabels': additional_labels
  };
  // Create a FileReader to read the file
  var reader = new FileReader();
  reader.readAsDataURL(file);

  reader.onloadend = function() {
  var base64data = reader.result;
  // Remove the prefix `data:file_type;base64,` from the result
  base64data = base64data.split(',')[1];

  var body = {
    image: base64data // Image data as base64 encoded string
  };

  return apigClient.uploadPut(params, body, additionalParams)
    .then(function (response) {
        console.log("Upload Response:", response);
        return response.data;
    }).catch(function (error) {
        console.error("Upload failed:", error);
        throw error;
    });
  

}
}