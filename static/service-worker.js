self.addEventListener('install', (event) => {
    console.log('Service worker installing...');
    // Put your install code here
  });
  
  self.addEventListener('fetch', function(event) {
    console.log('Fetching:', event.request.url);
    // Put your fetch handling logic here
  });