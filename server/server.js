const express = require('express');
const request = require('request');
var bodyParser = require('body-parser');

const app = express();

// Create application/x-www-form-urlencoded parser
var urlencodedParser = bodyParser.urlencoded({ extended: false })

app.use((req, res, next) => {
  res.header('Access-Control-Allow-Origin', '*');
  next();
});
/*
app.get('/foods_for_suggestion/_search', (req, res) => {
  request(
    { url: 'http://51.210.181.177:9200/foods_for_suggestion/_search' },
    (error, response, body) => {
      if (error || response.statusCode !== 200) {
        return res.status(500).json({ type: 'error', message: err.message });
      }
	  
      res.json(JSON.parse(body));
    }
  )
});
*/

app.post('/foods_for_suggestion/_search', urlencodedParser, function (req, res) {
   // Prepare output in JSON format
   //response = {
   //   first_name:req.body.first_name,
   //   last_name:req.body.last_name
   //};
   //console.log(response);
   //res.end(JSON.stringify(response));
   
   // payload
    var esData = '{"suggest":{"text":"' + searchedText + '","mysuggest":{"term":{"field":"food_description_suggest"}}}}';
	res.send(JSON.stringify(esData));
})

//const PORT = process.env.PORT || 3000;
//app.listen(PORT, () => console.log(`listening on ${PORT}`));

var server = app.listen(8081, function () {
   var host = server.address().address
   var port = server.address().port
   
   console.log("Example app listening at http://%s:%s", host, port)
})